from math import radians, tan
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

