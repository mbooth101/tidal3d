from app import App
from array import array
from buttons import _num
from math import radians, tan
from micropython import const
from tidal import *
from tidal3d import *
import time

from .buffdisp import BufferedDisplay
from .object import Mesh

MODE_POINT_CLOUD = const(0)
MODE_WIREFRAME_FULL = const(1)
MODE_WIREFRAME_BACK_FACE_CULLING = const(2)
MODE_SOLID = const(3)
MODE_SOLID_SHADED = const(4)


class Renderer(App):

    def __init__(self):
        super().__init__()

        # We'll render the scene to an off-screen buffer and blit it to the display
        # all at once when we're ready
        self.fb = BufferedDisplay(display)

        # Initial render mode and object, see the constants above for other modes
        self.render_mode = MODE_SOLID_SHADED
        self.render_object = 'cube.obj'

        # Projection matrix
        self.m_proj = Renderer.perspective_matrix(90, self.fb.width / self.fb.height,  0.1, 100)

        # Camera position and view transformation matrix
        # TODO a proper camera system
        self.v_campos = array('f', [0, 10, 35])
        self.m_view = Renderer.identity_matrix()
        m_translate(self.m_view, array('f', [0, -10, -35]))

        # Lighting vector
        self.v_light = array('f', [-1, -1, -2])
        v_normalise(self.v_light)

        # Model to render
        self.mesh = Mesh(self.render_object)

        self.start_t = 0
        self.accum_t = 0
        self.frame_counter = 0
        self.fps = 0

    @staticmethod
    def identity_matrix():
        """
        Returns the identity matrix, multiplication of any matrix M with the identity matrix will yield the
        original matrix M
        """
        return array('f', [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])

    @staticmethod
    def perspective_matrix(fov, aspect, near, far):
        """
        Returns the perspective projection matrix for the given field of view and aspect ratio, multiplication
        of any vector V with the projection matrix will yield normalised device coordinates
        """
        proj_mat = [0] * 16
        # Set the field of view, accomodating for the aspect ratio of the screen
        scale = tan(radians(fov * 0.5))
        proj_mat[0] = 1.0 / (scale * aspect)  # Scale of the x coord of the projected vertex
        proj_mat[5] = 1.0 / scale  # Scale of the y coord of the projected vertex
        # Z clipping planes
        proj_mat[10] = -far / (far - near)
        proj_mat[14] = -far * near / (far - near)
        # Setting these following values is how we do the perspective division, by causing w to be set to -z
        # instead of 1 and then w is used as the normalising divisor during vector-proj_mat multiplication
        proj_mat[11] = -1
        proj_mat[15] = 0

        return array('f', proj_mat)

    def on_activate(self):
        super().on_activate()

        # Register input callbacks
        self.buttons.on_press(BUTTON_A, self.select_mode)
        self.buttons.on_press(BUTTON_B, self.select_object)
        self.buttons.on_press(JOY_UP, self.button_up, False)
        self.buttons.on_press(JOY_DOWN, self.button_down, False)
        self.buttons.on_press(JOY_LEFT, self.button_left, False)
        self.buttons.on_press(JOY_RIGHT, self.button_right, False)

        self.start_t = time.ticks_us()
        self.loop()

    def on_deactivate(self):
        self.timer.cancel()
        super().on_deactivate()

    def select_mode(self):
        # Cycle through the render modes
        self.render_mode += 1
        if self.render_mode > MODE_SOLID_SHADED:
            self.render_mode = 0

    def select_object(self):
        # Cycle through objects to render
        if self.render_object == 'cube.obj':
            self.render_object = 'teapot.obj'
        elif self.render_object == 'teapot.obj':
            self.render_object = 'cube.obj'
        # Reload the model
        self.mesh = Mesh(self.render_object)

    def button_left(self):
        self.mesh.rotate_y(45)

    def button_right(self):
        self.mesh.rotate_y(-45)

    def button_up(self):
        self.mesh.rotate_x(45)

    def button_down(self):
        self.mesh.rotate_x(-45)

    def _get_button_state(self, pin):
        # Buttons are active so invert to make truthy mean pressed, which seems more intuitive
        return not self.buttons._callbacks[_num(pin)].state

    def loop(self):
        last_t = self.start_t
        self.start_t = time.ticks_us()
        delta_t = time.ticks_diff(self.start_t, last_t)

        # Update the simulation
        self.update(delta_t / 1000000)

        # Render the scene
        self.render_background()
        self.render_scene(self.render_mode)
        self.render_foreground()
        self.fb.blit()

        # Calculate frames per second
        self.frame_counter += 1
        self.accum_t += delta_t
        if self.accum_t > 1000000:
            self.accum_t -= 1000000
            self.fps = self.frame_counter
            self.frame_counter = 0

        # Show the time it took to render the frame
        print("{:,} us".format(delta_t))

        self.timer = self.after(1, self.loop)

    def update(self, delta_t):
        # Kill velocity if buttons no longer pressed
        if not self._get_button_state(JOY_LEFT) and not self._get_button_state(JOY_RIGHT):
            self.mesh.rotate_y(0)
        if not self._get_button_state(JOY_UP) and not self._get_button_state(JOY_DOWN):
            self.mesh.rotate_x(0)

        self.mesh.update(delta_t)

    def render_background(self):
        fb = self.fb

        # Just clear the framebuffer by filling it with a solid colour
        fb.rect(0, 0, fb.width, fb.height, BLACK, True)

        # Show some instructions on screen
        fb.text("A = RENDER MODE", 0, 0, WHITE)
        fb.text("B = NEXT OBJECT", 0, 10, WHITE)
        fb.text("JOY = ROTATE", 0, 20, WHITE)

    def render_scene(self, render_mode):
        fb = self.fb

        # Cached references to frequently accessed mesh properties
        mesh = self.mesh
        faces = mesh.faces
        verts = mesh.vertices_trans
        norms = mesh.normals_trans
        depth_map = mesh.depth_map

        # Transform all vertices to their positions in the world by multiplying by the model
        # transformation matrix, which is specific to the mesh being rendered (create world
        # coordinates)
        # Note that translating doesn't mean anything for vectors, so normals are rotated only,
        # and vertices are both rotated and translated
        m_model = Renderer.identity_matrix()
        m_rotate(m_model, mesh.orientation)
        v_multiply_batch(mesh.normals, m_model, norms)
        m_translate(m_model, mesh.position)
        v_multiply_batch(mesh.vertices, m_model, verts)

        # Pre-allocated space for intermediate calculations to minimise object instantiations,
        # which really helps with performance sensitive applications like this
        camera = array('f', [0, 0, 0])
        centre = array('f', [0, 0, 0])
        rgb = array('f', [0, 0, 0])
        coords = array('h', [0] * 6)
        face_verts = [None, None, None]

        # Generate a list of faces for rendering
        num_faces = 0
        for face_index in range(len(faces)):
            indices, norm_index, _ = faces[face_index]

            # Calculate the point in the centre of the face
            face_verts[0] = verts[indices[0]]
            face_verts[1] = verts[indices[1]]
            face_verts[2] = verts[indices[2]]
            v_average(face_verts, centre)

            # Calculate the the direction to the camera from the centre of the face
            v_subtract(self.v_campos, centre, camera)
            v_normalise(camera)

            # Now we use the dot product to determine if the front of the face is pointing at the
            # camera; if the angle between the normal vector and the camera vector is greater than
            # 90 degrees then we are seeing the back of the face, and if we are culling back faces
            # then we can avoid rendering it
            dot = v_dot(norms[norm_index], camera)
            if (dot < 0 and render_mode >= MODE_WIREFRAME_BACK_FACE_CULLING):
                continue

            # Record the face for rendering along with its average depth from the camera, the face's
            # depth is the z component of the centre point transformed by the camera view matrix
            v_multiply(centre, self.m_view)
            depth_map[num_faces * 2] = face_index
            depth_map[num_faces * 2 + 1] = centre[2]
            num_faces += 1

        # A painter's algorithm; use the face's average depth value to order them from back to front,
        # this ensures far away faces are not drawn on top of near faces
        z_sort(depth_map, num_faces)

        # Since faces can share vertices, and matrix multiplication is expensive, let's not project
        # a vertex more than once, we'll just keep a list of vertices that we've already projected
        projected_verts = [False] * len(mesh.vertices)

        # Render faces
        m_view = self.m_view
        m_proj = self.m_proj
        for i in range(0, num_faces * 2, 2):
            face_index = int(depth_map[i])
            indices, norm_index, col_index = faces[face_index]

            visible = False

            # Let's go ahead and project the face's vertices
            for j in range(3):
                index = indices[j]
                vertex = verts[index]

                # Only project a vertex if we've not already done so
                if not projected_verts[index]:
                    projected_verts[index] = True

                    # Transform the world coorinates into camera coordinates by multiplying by the
                    # camera view matrix, allowing it be viewed from the camera's point of view
                    v_multiply(vertex, m_view)

                    # Project the vertex onto a 2D plane by multiplying by the projection matrix, this
                    # yields normalised device coords where all points that lie within the viewable
                    # space defined by the field of view are mapped to between -1.0, 1.0
                    # The projection matrix multiplication also performs the perspective division,
                    # which makes more distant points appear further away by making them closer together
                    # on the x and y axes
                    v_multiply(vertex, m_proj)

                # If a face's projected vertices all lie outside the viewable space (x or y is more
                # than 1 or less then -1) then we can cull it because it will not be seen; if at least
                # one vertex can be seen, we'll render the partial face
                if vertex[0] > -1 and vertex[0] < 1 and vertex[1] > -1 and vertex[1] < 1:
                    visible = True

                face_verts[j] = vertex

            # If none of this face's vertices can be seen, continue to the next face
            if not visible:
                continue

            # Convert normalised device coordinates (NDCs) to screen coordinates, if an NDC's x and y
            # components both lie between -1 and 1, it will result in a valid on-screen pixel location
            # This is implemented in native code for speed reasons, but it just does this:
            #        x = (v[0] + 1) * 0.5 * width
            #        y = (1 - (v[1] + 1) * 0.5) * height
            # Obviously the y axis here is inverted because screens tend to have the origin 0,0 at the
            # top left and increases towards the bottom
            v_ndc_to_screen(face_verts, coords, fb.width, fb.height)

            colour = WHITE
            if render_mode > MODE_POINT_CLOUD and render_mode < MODE_SOLID_SHADED:
                # Solid, unshaded colour
                v_scale(mesh.colours[col_index], 1, rgb)
                colour = color565(int(rgb[0]), int(rgb[1]), int(rgb[2]))
            elif render_mode >= MODE_SOLID_SHADED:
                # Scale the color by the angle of incidence of the light vector so a face appears
                # more brightly lit the closer to orthogonal it is, but clamp to a minimum value
                # so unlit faces are not totally invisible, simulating a bit of ambient light
                dot = v_dot(norms[norm_index], self.v_light)
                v_scale(mesh.colours[col_index], -dot, rgb)
                colour = color565(max(int(rgb[0]), 8), max(int(rgb[1]), 8), max(int(rgb[2]), 8))

            # Draw to the framebuffer using screen coordinates
            if render_mode == MODE_POINT_CLOUD:
                fb.points(coords, colour)
            elif render_mode == MODE_WIREFRAME_FULL or render_mode == MODE_WIREFRAME_BACK_FACE_CULLING:
                fb.polygon(coords, colour)
            elif render_mode >= MODE_SOLID:
                fb.polygon(coords, colour, True)

    def render_foreground(self):
        self.fb.text("{0:2d} fps".format(self.fps), 0, self.fb.height - 10, WHITE)


# Set the entrypoint for the app launcher
main = Renderer
