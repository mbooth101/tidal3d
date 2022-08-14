from framebuf import FrameBuffer, RGB565
from array import array


class BufferedDisplay(FrameBuffer):
    """
    A buffered display that renders to an off-screen framebuffer so the whole scene can be blitted to the
    actual display in one call

    Also wraps drawing calls where it provides extra convenience and provides some extra drawing calls not
    implemented by the underlying framebuffer or display
    """

    def __init__(self, display):
        self.display = display

        # Cache screen dimensions
        self.width = display.width()
        self.height = display.height()

        # Create a framebuffer the same size as the display
        self.buffer = bytearray(2 * self.width * self.height)
        super().__init__(self.buffer, self.width, self.height, RGB565)

    def swap_colour_bytes(self, colour):
        """
        The byte-order of the built-in framebuffer appears to be the opposite endianness to that of the
        physical display, so this utility function swaps the two bytes of the given colour value
        """
        b1 = colour & 0xff
        b2 = (colour >> 8) & 0xff
        return (b1<<8) | b2

    def chequerboard(self, size, dark_colour, light_colour):
        """
        Draws a chequerboard pattern to the framebuffer with squares of the given size and alternating
        colours
        """
        dark_colour = self.swap_colour_bytes(dark_colour)
        light_colour = self.swap_colour_bytes(light_colour)
        x = 0
        while x < self.width:
            y = 0
            while y < self.height:
                if (x / size) % 2 != (y / size) % 2:
                    colour = dark_colour
                else:
                    colour = light_colour
                self.rect(x, y, size, size, colour, True)
                y += size
            x += size

    def points(self, points, colour):
        """
        Draw the given list of points to the framebuffer
        """
        colour = self.swap_colour_bytes(colour)
        self.pixel(points[0], points[1], colour)
        self.pixel(points[2], points[3], colour)
        self.pixel(points[4], points[5], colour)

    def polygon(self, points, colour, fill=False):
        """
        Draw the given list of points to the framebuffer as a closed, optionally filled, polygon
        """
        colour = self.swap_colour_bytes(colour)
        self.poly(0, 0, array('h', points), colour, fill)

    def blit(self):
        """
        Send the framebuffer to the display
        """
        self.display.blit_buffer(self.buffer, 0, 0, self.width, self.height)
