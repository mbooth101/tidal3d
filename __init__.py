from tidal import *
from app import App
import framebuf
import time

class BufferedDisplay:
    """A buffered display that renders to an off-screen framebuffer so the whole scene can
    be blitted to the actual display in one call"""

    def __init__(self, display):
        self.display = display

        # Cache screen dimensions
        self.width = display.width()
        self.height = display.height()

        # Create a framebuffer the same size as the display
        self.buffer = bytearray(2 * self.width * self.height)
        self.fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.RGB565)

    def chequerboard(self, size, dark_colour, light_colour):
        """Renders a chequerboard pattern to the framebuffer"""
        x = 0
        while x < self.width:
            y = 0
            while y < self.height:
                if (x / size) % 2 != (y / size) % 2:
                    colour = dark_colour
                else:
                    colour = light_colour
                self.fb.fill_rect(x, y, size, size, colour)
                y += size
            x += size

    def blit(self):
        """Send the framebuffer to the display"""
        self.display.blit_buffer(self.buffer, 0, 0, self.width, self.height)

class Renderer(App):

    def __init__(self):
        super().__init__()

        # We'll render the frame to an off-screen buffer and blit it to the display
        # all at once when we're ready
        self.fb = BufferedDisplay(display)

    def on_activate(self):
        super().on_activate()

        self.render()
        self.timer = self.periodic(1000, self.render)

    def on_deactivate(self):
        self.timer.cancel()
        super().on_deactivate()

    def render(self):
        a = time.ticks_ms()
        # Render background
        self.fb.chequerboard(15, color565(185, 185, 185), color565(235, 235, 235))

        # Render foreground
        # TODO

        self.fb.blit()
        b = time.ticks_ms()
        print(time.ticks_diff(b,a))

# Set the entrypoint for the app launcher
main = Renderer

