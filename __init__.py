from tidal import *
from app import App
from buttons import _num
import time

from .buffdisp import BufferedDisplay
from .math3d import Vec, Mat

MODE_POINTS = 0
MODE_WIREFRAME = 1

class Mesh:

    def __init__(self, vertices=None, indices=None):
        # Use a default mesh of a cube
        self.vertices = [Vec([-10, -10, 10]), Vec([-10, 10, 10]), Vec([10, 10, 10]), Vec([10, -10, 10]), Vec([-10, -10, -10]), Vec([-10, 10, -10]), Vec([10, 10, -10]), Vec([10, -10, -10])]
        self.indices = [[0, 1, 2], [2, 3, 0], [1, 5, 6], [6, 2, 1], [5, 4, 7], [7, 6, 5], [4, 0, 3], [3, 7, 4], [3, 2, 6], [6, 7, 3], [0, 5, 1], [0, 4, 5]]

        # Position and velocity information
        self.pos = Vec([0, 0, 0])
        self.velocity = Vec([0, 0, 0])

    def update(self):
        # Move our position by our velocity
        self.pos = self.pos.add(self.velocity)


class Renderer(App):

    def __init__(self):
        super().__init__()

        # We'll render the scene to an off-screen buffer and blit it to the display
        # all at once when we're ready
        self.fb = BufferedDisplay(display)

        # Initial render mode, see the constants above for other modes
        self.render_mode = MODE_POINTS

        # Projection matrix
        self.m_proj = Mat.perspective(90, self.fb.width / self.fb.height,  0.1, 100)

        # Camera view transformation matrix
        self.m_view = Mat.identity().translate(Vec([0, 0, -35]))

        # Model to render
        self.mesh = Mesh()

    def on_activate(self):
        super().on_activate()

        # Register input callbacks
        self.buttons.on_press(BUTTON_A, self.select_mode)
        self.buttons.on_press(JOY_UP, self.button_up, False)
        self.buttons.on_press(JOY_DOWN, self.button_down, False)
        self.buttons.on_press(JOY_LEFT, self.button_left, False)
        self.buttons.on_press(JOY_RIGHT, self.button_right, False)

        self.loop()
        self.timer = self.periodic(100, self.loop)

    def on_deactivate(self):
        self.timer.cancel()
        super().on_deactivate()

    def select_mode(self):
        # Cycle through the render modes
        if self.render_mode == MODE_POINTS:
            self.render_mode = MODE_WIREFRAME
        elif self.render_mode == MODE_WIREFRAME:
            self.render_mode = MODE_POINTS

    def button_left(self):
        self.mesh.velocity[0] = -0.5

    def button_right(self):
        self.mesh.velocity[0] = 0.5

    def button_up(self):
        self.mesh.velocity[1] = 0.5

    def button_down(self):
        self.mesh.velocity[1] = -0.5

    def _get_button_state(self, pin):
        # Buttons are active so invert to make truthy mean pressed, which seems more intuitive
        return not self.buttons._callbacks[_num(pin)].state

    def loop(self):
        start_t = time.ticks_ms()

        # Update the simulation
        self.update()

        # Render the scene
        self.render_background()
        self.render_scene()
        self.fb.blit()

        end_t = time.ticks_ms()
        # Show the time it took to render the scene
        print(time.ticks_diff(end_t, start_t))

    def update(self):
        # Kill velocity if buttons no longer pressed
        if not self._get_button_state(JOY_LEFT) and not self._get_button_state(JOY_RIGHT):
            self.mesh.velocity[0] = 0
        if not self._get_button_state(JOY_UP) and not self._get_button_state(JOY_DOWN):
            self.mesh.velocity[1] = 0

        self.mesh.update()

    def render_background(self):
        # Just clear the framebuffer by filling it with a solid colour
        self.fb.fb.fill_rect(0, 0, self.fb.width, self.fb.height, BLACK)

        # Show some instructions on screen
        self.fb.fb.text("A = Render Mode", 0, 0, WHITE)

    def render_scene(self):
        # Model transformation matrix, specific to the mesh being rendered
        m_model = Mat.identity().translate(self.mesh.pos)

        # Project all verts in the model
        verts = []
        for v in self.mesh.vertices:

            # Transform the vertex to its position in the world by multiplying by the model matrix
            v_world = v.multiply(m_model)

            # Transform the world so it is viewed appropriately by the camera by multiplying by the
            # camera view matrix
            v_cam = v_world.multiply(self.m_view)

            # Project the vertex onto a 2D plane by multiplying by the projection matrix, this yields
            # normalised device coords where all points that lie within the viewable space defined by
            # the field of view are mapped to between -1.0, 1.0
            # The projection matrix multiplication also performs the perspective division, which makes
            # more distant points appear further away by making them closer together on the x and y axes
            v_ndc = v_cam.multiply(self.m_proj)
            verts.append(v_ndc)

        # Render faces
        for face in self.mesh.indices:
            # If a face's projected vertices all lie outside the viewable space (x or y is more than 1
            # or less then -1) then we can cull it because it will not be seen; if at least one vertex
            # can be seen, we'll render the partial face
            visible = False
            face_verts = [verts[i] for i in face]
            for face_vert in face_verts:
                if face_vert[0] > -1 and face_vert[0] < 1 and face_vert[1] > -1 and face_vert[1] < 1:
                    visible = True
                    break
            if not visible:
                continue

            # Now we take the x,y components of the normalised device coords and convert them into
            # screen coords, obviously inverting y because screens tend to have 0,0 at the top left
            coords = []
            for face_vert in face_verts:
                x = (face_vert[0] + 1) * 0.5 * self.fb.width
                y = (1 - (face_vert[1] + 1) * 0.5) * self.fb.height
                coords.append([x, y])

            # Write to framebuffer
            if self.render_mode == MODE_POINTS:
                for coord in coords:
                    self.fb.pixel(coord, WHITE)
            elif self.render_mode == MODE_WIREFRAME:
                self.fb.triangle(coords[0], coords[1], coords[2], WHITE)


# Set the entrypoint for the app launcher
main = Renderer

