from st7789 import color565, WHITE

from .math3d import Vec, Mat, Quat


class Mesh:

    def __init__(self, filename):
        # A face is made of 3 vertices, a normal vector, and a material
        self.vertices = []
        self.normals = []
        self.colours = []

        # To prevent duplication of data (and therefore saving on expensive memory and calculation
        # time) we store each unique vertex, normal and material once and instead keep per-face
        # indices into the above lists
        self.vert_indices = []
        self.norm_indices = []
        self.col_indices = []

        # Load mesh and material data
        self._load(filename)

        # Position and linear velocity
        self.position = Vec([0, 0, 0])
        self.velocity = Vec([0, 0, 0])

        # Orientation and angular velocity
        self.orientation = Quat([1, 0, 0, 0])
        self.angular = Vec([0, 0, 0])

    def _load(self, filename):
        # Parse the geometry file
        op = ObjectParser()
        op.parse("apps/TiDAL3D/" + filename)

        self.vertices = [Vec(v) for v in op.vertices]
        self.vert_indices = [f['indices'] for f in op.faces]

        # Pre-calculate face normal vectors, a normal is the direction exactly perpendicular to
        # the plane of the face, the direction the front of the face is pointing
        for face in self.vert_indices:
            a = self.vertices[face[0]]
            b = self.vertices[face[1]]
            c = self.vertices[face[2]]
            normal = a.subtract(b).cross(b.subtract(c)).normalise()
            if normal not in self.normals:
                self.normals.append(normal)
            self.norm_indices.append(self.normals.index(normal))

        # If the geometry has materials, let's also parse the accompanying material library file
        if op.mat_lib:
            mp = MaterialParser()
            mp.parse("apps/TiDAL3D/" + op.mat_lib)

            # Use the material's diffuse colour for the colour of the faces, pre-computing the
            # 16-bit 565 value that our display needs from RGB values
            self.col_indices = [0] * len(self.vert_indices)
            for material in mp.materials:
                rgb = material['diffuse']
                self.colours.append(color565(rgb[0], rgb[1], rgb[2]))
                for i in range(len(op.faces)):
                    if op.faces[i]['material'] == material['name']:
                        self.col_indices[i] = len(self.colours) - 1
        else:
            # Just default to all white faces if no materials specified
            self.colours.append(WHITE)
            self.col_indices = [0] * len(self.vert_indices)

    def update(self):
        # Move our position by our velocity
        self.position = self.position.add(self.velocity)
        # Rotate ourselves around the axis
        degrees = self.angular.mag()
        axis = self.angular.normalise()
        self.orientation = self.orientation.rotate(degrees, axis)


class ParserInterface:
    """
    General interface for Wavefront geometry style file parsers, each non-comment line is tokenised
    and then passed into the parameter method for decoding; sub-classes implement the parameter
    method according to the specific file type they want to parse; the finish method will be called
    when the end of the file is reached
    """

    def parameter(self, name, values):
        pass

    def finish(self):
        pass

    def parse(self, file):
        with open(file) as f:
            while line := f.readline():
                # Ignore comments and empty lines
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                tokens = line.split()
                # Decode the parameter
                self.parameter(tokens[0], tokens[1:])
            # Do any tidy up the parser needs to do
            self.finish()


class ObjectParser(ParserInterface):
    """
    A parser for Wavefront object geometry files (*.obj)
    """

    def __init__(self):
        self.mat_lib = None
        self.current_mat = None
        self.vertices = []
        self.faces = []

    def parameter(self, name, values):
        # This gives the file containing the material library
        if name == 'mtllib':
            self.mat_lib = values[0]
        # Set the active material for the following faces
        if name == 'usemtl':
            self.current_mat = values[0]
        # Extract a vertex
        if name == 'v':
            self.vertices.append([float(v) for v in values])
        # Extract a face
        if name == 'f':
            # Faces are given as "vert_index/uv_index/normal_index" triplets but we don't support
            # texturing, so ignore the uv part, and we don't support anything other than flat shading,
            # so ignore the vertex normals part -- since we know face vertices have anti-clockwise
            # winding, we can just calculate face normals ourselves
            vert_indices = [int(a.split('/')[0]) - 1 for a in values]

            face = {'material':self.current_mat, 'indices':vert_indices}
            self.faces.append(face)


class MaterialParser(ParserInterface):
    """
    A parser for Wavefront material library files (*.mtl)
    """

    def __init__(self):
        self.materials = []
        self.current = None

    def parameter(self, name, values):
        # A new material is being defined
        if name == 'newmtl':
            if self.current:
                self.materials.append(self.current)
            self.current = {'name' : values[0]}
        # Extract the diffuse colour (base colour in Blender)
        if name == 'Kd':
            # RGB values are given as floating point values between 0 and 1, so convert them here
            # to byte values between 0 and 255
            self.current['diffuse'] = [int(255 if float(f) >= 1 else float(f) * 256) for f in values]

    def finish(self):
        self.materials.append(self.current)
        self.current = None
