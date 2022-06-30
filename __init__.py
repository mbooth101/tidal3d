from tidal import *
from app import App
import time

from .buffdisp import BufferedDisplay
from .math3d import Vec, Mat


class Mesh:

    def __init__(self, vertices=None, indices=None):
        # Use a default mesh of a cube
        self.vertices = [Vec([-1, -1, 1]), Vec([-1, 1, 1]), Vec([1, 1, 1]), Vec([1, -1, 1]), Vec([-1, -1, -1]), Vec([-1, 1, -1]), Vec([1, 1, -1]), Vec([1, -1, -1])]
        # self.indices = ((0, 1, 2), (2, 3, 0), (1, 5, 6), (6, 2, 1), (5, 4, 7), (7, 6, 5), (4, 0, 3), (3, 7, 4), (3, 2, 6), (6, 7, 3), (0, 5, 1), (0, 4, 5))

        # Positional information
        self.pos = Vec([0, 0, 0])


class Renderer(App):

    def __init__(self):
        super().__init__()

        # We'll render the frame to an off-screen buffer and blit it to the display
        # all at once when we're ready
        self.fb = BufferedDisplay(display)

        # Projection matrix
        self.m_proj = Mat.perspective(90, 0.1, 100)

        # Camera view transformation matrix
        self.m_view = Mat.identity().translate(Vec([0, 0, -3]))

        # Model to render
        self.mesh = Mesh()

    def on_activate(self):
        super().on_activate()

        self.render()
        self.timer = self.periodic(100, self.render)

    def on_deactivate(self):
        self.timer.cancel()
        super().on_deactivate()

    def render(self):
        start = time.ticks_ms()
        self.render_background()
        self.render_scene()
        self.fb.blit()
        end = time.ticks_ms()
        # Show the time it took to render the frame
        print(time.ticks_diff(end, start))

    def render_background(self):
        # Just clear the framebuffer by filling it with a solid colour
        self.fb.fb.fill_rect(0, 0, self.fb.width, self.fb.height, BLACK)

    def render_scene(self):
        # Model transformation matrix, specific to the mesh being rendered
        m_model = Mat.identity().translate(self.mesh.pos)

        for v in self.mesh.vertices:

            # Transform the vertex to its position in the world by multiplying by the model matrix
            v_world = v.multiply(m_model)

            # Transform the world so it is viewed appropriately by the camera by multiplying by the
            # camera view matrix
            v_cam = v_world.multiply(self.m_view)

            # Project the vertex onto a 2D plane by multiplying by the projection matrix
            v_ndc = v_cam.multiply(self.m_proj)

            # Multiplying by the projection matrix yields normalised device coords where all points
            # that lie within the viewable space defined by the field of view are mapped to between
            # -1.0, 1.0 -- any points outside that space will be mapped to less than -1.0 or higher
            # than 1.0 and can be discarded because they cannot be seen
            # The projection matrix also performs the perspective division, which makes more distant
            # points appear further away by making them closer together on the x and y axes
            if v_ndc[0] < -1 or v_ndc[0] > 1 or v_ndc[1] < -1 or v_ndc[1] > 1:
                continue

            # Now we take the x,y components of the normalised device coords and convert them into
            # screen coords, obviously inverting y because screens tend to have 0,0 at the top left
            x = (v_ndc[0] + 1) * 0.5 * self.fb.width
            y = (1 - (v_ndc[1] + 1) * 0.5) * self.fb.height
            self.fb.pixel(x, y, WHITE)


# Set the entrypoint for the app launcher
main = Renderer

