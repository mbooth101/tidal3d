from functools import reduce
from math import cos, sin, radians, sqrt, tan


class Vec:
    """
    Utility class for dealing with 3D points and vectors
    """

    def __init__(self, v):
        self._v = v

    def __getitem__(self, index):
        return self._v[index]

    def __setitem__(self, index, value):
        self._v[index] = value

    def __eq__(self, other):
        return self._v == other._v

    def __str__(self):
        return 'Vec({}, {}, {})'.format(self._v[0], self._v[1], self._v[2])

    @staticmethod
    def average(vectors):
        """
        Returns the vector that is the average of the list of given vectors
        """
        x, y, z = (0, 0, 0)
        for v in vectors:
            x += v[0]
            y += v[1]
            z += v[2]
        num = len(vectors)
        return Vec([x / num, y / num, z / num])

    def mag(self):
        """
        Returns the magnitude of the vector as a scalar value
        """
        return sqrt(sum([a ** 2 for a in self._v]))

    def normalise(self):
        """
        Returns the vector normalised to unit length
        """
        magnitude = self.mag()
        if magnitude == 0:
            return Vec([0, 0, 0])
        else:
            return Vec([self[0] / magnitude, self[1] / magnitude, self[2] / magnitude])

    def scale(self, factor):
        """
        Returns the vector scaled by the given factor
        """
        return Vec([self[0] * factor, self[1] * factor, self[2] * factor])

    def add(self, vector):
        """
        Returns the vector given by the sum of this vector and the given vector
        """
        return Vec([self[0] + vector[0], self[1] + vector[1], self[2] + vector[2]])

    def subtract(self, vector):
        """
        Returns the vector given by subtracting the given vector from this vector
        """
        return Vec([self[0] - vector[0], self[1] - vector[1], self[2] - vector[2]])

    def multiply(self, matrix):
        """
        Returns the vector given by multiplying this vector by the given matrix
        """
        x = self[0] * matrix[0, 0] + self[1] * matrix[1, 0] + self[2] * matrix[2, 0] + matrix[3, 0]
        y = self[0] * matrix[0, 1] + self[1] * matrix[1, 1] + self[2] * matrix[2, 1] + matrix[3, 1]
        z = self[0] * matrix[0, 2] + self[1] * matrix[1, 2] + self[2] * matrix[2, 2] + matrix[3, 2]
        w = self[0] * matrix[0, 3] + self[1] * matrix[1, 3] + self[2] * matrix[2, 3] + matrix[3, 3]
        # Avoid doing the division if it wouldn't change the result
        if w == 1:
            return Vec([x, y, z])
        return Vec([x / w, y / w, z / w])

    def dot(self, vector):
        """
        Returns a scalar value of 0 if this vector and the given vector are exactly perpendicular, <0 if the
        angle between them is greater than 90° or >0 if the angle between them is less than 90° (dot product)
        """
        result = 0
        for i in range(3):
            # Micropython does not have math.prod(), so use reduce with a lambda instead
            result += reduce(lambda a, b: a * b, [v[i] for v in [self, vector]])
        return result

    def cross(self, vector):
        """
        Returns the vector that is perpendicular to both this vector and the given vector (cross product)
        """
        x = self[1] * vector[2] - self[2] * vector[1]
        y = self[2] * vector[0] - self[0] * vector[2]
        z = self[0] * vector[1] - self[1] * vector[0]
        return Vec([x, y, z])


class Quat:
    """
    Utility class for dealing with quaternions
    """

    def __init__(self, q):
        self._q = q

    def __getitem__(self, index):
        return self._q[index]

    def __setitem__(self, index, value):
        self._q[index] = value

    def __eq__(self, other):
        return self._q == other._q

    def __str__(self):
        return 'Quat({}, {}, {}, {})'.format(self._q[0], self._q[1], self._q[2], self._q[3])

    def rotate(self, angle, vector):
        """
        Returns the quaternion given by rotating this quaternion by the given angle of rotation in
        degrees around the axis described by the given vector
        """
        theta = radians(angle) / 2
        factor = sin(theta)
        rotation = Quat([cos(theta), vector[0] * factor, vector[1] * factor, vector[2] * factor])
        return self.multiply(rotation)

    def multiply(self, quat):
        """
        Returns the quaternion given by multiplying this quaternion with the given quaternion
        """
        w = self[0] * quat[0] - self[1] * quat[1] - self[2] * quat[2] - self[3] * quat[3]
        x = self[0] * quat[1] + self[1] * quat[0] + self[2] * quat[3] - self[3] * quat[2]
        y = self[0] * quat[2] - self[1] * quat[3] + self[2] * quat[0] + self[3] * quat[1]
        z = self[0] * quat[3] + self[1] * quat[2] - self[2] * quat[1] + self[3] * quat[0]
        return Quat([w, x, y, z])


class Mat:
    """
    Utility class for dealing with 4x4 matrices
    """

    def __init__(self, m):
        self._m = m

    def __getitem__(self, indices):
        x, y = indices
        return self._m[x][y]

    def __setitem__(self, indices, value):
        x, y = indices
        self._m[x][y] = value

    @staticmethod
    def identity():
        """
        Returns the identity matrix, multiplication of any matrix M with the identity matrix will yield the
        original matrix M
        """
        return Mat([[1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]])

    @staticmethod
    def perspective(fov, aspect, near, far):
        """
        Returns the perspective projection matrix for the given field of view and aspect ratio, multiplication
        of any vector V with the projection matrix will yield normalised device coordinates
        """
        proj_mat = Mat.identity()
        # Field of view, accomodating for the aspect ratio of the screen
        scale = tan(radians(fov * 0.5));
        proj_mat[0, 0] = 1.0 / (scale * aspect)  # Scale of the x coord of the projected vertex
        proj_mat[1, 1] = 1.0 / scale  # Scale of the y coord of the projected vertex
        # Z clipping planes
        proj_mat[2, 2] = -far / (far - near)
        proj_mat[3, 2] = -far * near / (far - near)
        # Setting these following values is how we do the perspective division, by causing w to be set to -z
        # instead of 1 and then w is used as the normalising divisor during vector-proj_mat multiplication
        proj_mat[2, 3] = -1
        proj_mat[3, 3] = 0

        return proj_mat

    def translate(self, vector):
        """
        Returns the matrix given by translating this matrix by the given vector
        """
        trans_mat = Mat.identity()
        trans_mat[3, 0] = vector[0]
        trans_mat[3, 1] = vector[1]
        trans_mat[3, 2] = vector[2]
        return self.multiply(trans_mat)

    def rotate(self, quaternion):
        """
        Returns the matrix given by rotating this matrix by the given quaternion
        """
        w, x, y, z = [quaternion[i] for i in range(4)]
        rot_mat = Mat.identity()
        rot_mat[0, 0] = 1 - 2 * (y * y + z * z)
        rot_mat[0, 1] = 2 * (x * y - w * z)
        rot_mat[0, 2] = 2 * (x * z + w * y)
        rot_mat[1, 0] = 2 * (x * y + w * z)
        rot_mat[1, 1] = 1 - 2 * (x * x + z * z)
        rot_mat[1, 2] = 2 * (y * z - w * x)
        rot_mat[2, 0] = 2 * (x * z - w * y)
        rot_mat[2, 1] = 2 * (y * z + w * x)
        rot_mat[2, 2] = 1 - 2 * (x * x + y * y)
        return self.multiply(rot_mat)

    def multiply(self, matrix):
        """
        Returns the matrix given by multiplying this matrix by the given matrix
        """
        result = [[0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0]]
        # We are assuming here that both operands are 4x4 matrices, but you could make these loops work for
        # multiplying arbitrarily sized matrices if the number of rows on the LHS is equal to the number of
        # columns on the RHS
        for i in range(4):  # num of rows on the LHS
            for j in range(4):  # num of cols on the RHS
                result[i][j] += self[i, 0] * matrix[0, j]
                result[i][j] += self[i, 1] * matrix[1, j]
                result[i][j] += self[i, 2] * matrix[2, j]
                result[i][j] += self[i, 3] * matrix[3, j]
        return Mat(result)
