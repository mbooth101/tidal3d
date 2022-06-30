from functools import reduce
from math import sqrt, tan, pi


class Vec:
    """
    Utility class for dealing with points and vectors
    """

    def __init__(self, v):
        self._v = v

    def __getitem__(self, index):
        return self._v[index]

    def __setitem__(self, index, value):
        self._v[index] = value

    def mag(self):
        """
        Returns the magnitude of the vector as a scalar value
        """
        return sqrt(sum([a ** 2 for a in self._v]))

    def normalise(self):
        """
        Returns the vector normalised to unit length
        """
        return Vec([a / self.mag() for a in self._v])

    def scale(self, factor):
        """
        Returns the vector scaled by the given factor
        """
        return Vec([a * factor for a in self._v])

    def multiply(self, matrix):
        """
        Returns the vector given by multiplying this vector by the given matrix
        """
        x = self[0] * matrix[0, 0] + self[1] * matrix[1, 0] + self[2] * matrix[2, 0] + matrix[3, 0]
        y = self[0] * matrix[0, 1] + self[1] * matrix[1, 1] + self[2] * matrix[2, 1] + matrix[3, 1]
        z = self[0] * matrix[0, 2] + self[1] * matrix[1, 2] + self[2] * matrix[2, 2] + matrix[3, 2]
        w = self[0] * matrix[0, 3] + self[1] * matrix[1, 3] + self[2] * matrix[2, 3] + matrix[3, 3]
        return Vec([x / w, y / w, z / w])

    def dot(self, vector):
        """
        Returns a scalar value of 0 if this vector and the given vector are exactly perpendicular, <0 if the
        angle between them is greater than 90° or >0 if the angle between them is less than 90° (dot product)
        """
        result = 0
        # We are assuming here that both operands are vectors of the same length
        for i in range(len(self._v)):
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
    def perspective(fov, near, far):
        """
        Returns the perspective projection matrix for the given field of view, multiplication of any vector V
        with the projection matrix will yield normalised device coordinates
        """
        proj_mat = Mat.identity()
        # Field of view
        scale = 1 / tan(fov * 0.5 * pi / 180);
        proj_mat[0, 0] = scale
        proj_mat[1, 1] = scale
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
        Returns the matrix translated by the given amounts along the 3 axes
        """
        trans_mat = Mat.identity()
        trans_mat[3, 0] = vector[0]
        trans_mat[3, 1] = vector[1]
        trans_mat[3, 2] = vector[2]
        return self.multiply(trans_mat)

    def rotate(self, degrees, x, y, z):
        """
        Returns the matrix rotated by the given degrees about the 3 axes
        """
        rot_mat = Mat.identity()
        # TODO
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
                for k in range(4):  # num of rows on the RHS
                    result[i][j] += self[i, k] * matrix[k, j]
        return Mat(result)
