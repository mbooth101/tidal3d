from math import cos, sin, radians, tan
from tidal3d import *


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
