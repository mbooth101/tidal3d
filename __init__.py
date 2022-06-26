from tidal import *
from app import App

class Renderer(App):

    # Cache screen dimensions
    DISPLAY_WIDTH = display.width()
    DISPLAY_HEIGHT = display.height()
    
    def __init__(self):
        super().__init__()

        # Pre-render the background to an off-screen buffer the same size as the display
        # Blitting is about twice as fast and re-rendering the chequerboard directly to
        # the screen on every frame
        self.bg_buffer = bytearray(2 * self.DISPLAY_WIDTH * self.DISPLAY_HEIGHT)
        self.chequerboard(self.bg_buffer, 15, color565(175, 175, 175), color565(235, 235, 235))

    # Like display.fill_rect(), but for the given buffer
    def fill_rect(self, buffer, x, y, width, height, colour):
        colour_bytes = colour.to_bytes(2, 'big')
        for h in range(height):
            origin = (x * 2) + ((y + h) * self.DISPLAY_WIDTH * 2)
            for px in range(origin, origin + (width * 2), 2):
                buffer[px] = colour_bytes[0]
                buffer[px+1] = colour_bytes[1]

    # Renders a chequerboard pattern to the given buffer
    def chequerboard(self, buffer, square_size, dark_colour, light_colour):
        x = 0
        while x < self.DISPLAY_WIDTH:
            y = 0
            while y < self.DISPLAY_HEIGHT:
                if (x / square_size) % 2 != (y / square_size) % 2:
                    colour = dark_colour
                else:
                    colour = light_colour
                self.fill_rect(buffer, x, y, square_size, square_size, colour)
                y += square_size
            x += square_size

    def on_activate(self):
        super().on_activate()
        self.render()
        self.timer = self.periodic(1000, self.render)

    def on_deactivate(self):
        self.timer.cancel()
        super().on_deactivate()

    def render(self):
        # Render the background (~32 or 33ms)
        display.blit_buffer(self.bg_buffer, 0, 0, self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)

# Set the entrypoint for the app launcher
main = Renderer

