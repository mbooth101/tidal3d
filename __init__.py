from tidal import *
from app import App

class Renderer(App):

    DISPLAY_WIDTH = display.width()
    DISPLAY_HEIGHT = display.height()
    
    def __init__(self):
        super().__init__()

    def on_activate(self):
        super().on_activate()
        self.render()
        self.timer = self.periodic(1000, self.render)
    
    def on_deactivate(self):
        self.timer.cancel()
        super().on_deactivate()

    def render(self):
        dark_colour = color565(175, 175, 175)
        light_colour = color565(235, 235, 235)
        square_size = 15

        x = 0
        while x < self.DISPLAY_WIDTH:
            y = 0
            while y < self.DISPLAY_HEIGHT:
                if (x / square_size) % 2 != (y / square_size) % 2:
                    colour = dark_colour
                else:
                    colour = light_colour

                display.fill_rect(x, y, square_size, square_size, colour)
                y += square_size

            x += square_size

# Set the entrypoint for the app launcher
main = Renderer

