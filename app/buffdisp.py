from framebuf import FrameBuffer, RGB565


class BufferedDisplay:
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
        self.fb = FrameBuffer(self.buffer, self.width, self.height, RGB565)

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
                self.fb.fill_rect(x, y, size, size, colour)
                y += size
            x += size

    def points(self, points, colour):
        """
        Draw the given list of points to the framebuffer
        """
        colour = self.swap_colour_bytes(colour)
        for point in points:
            self.fb.pixel(point[0], point[1], colour)

    def polygon(self, points, colour):
        """
        Draw the given list of points to the framebuffer as a closed polygon
        """
        colour = self.swap_colour_bytes(colour)
        self.fb.polygon(points, 0, 0, colour)

    def fill_polygon(self, points, colour):
        """
        Draw the given list of points to the framebuffer as a filled, closed polygon
        """
        colour = self.swap_colour_bytes(colour)
        self.fb.fill_polygon(points, 0, 0, colour)

    def blit(self):
        """
        Send the framebuffer to the display
        """
        self.display.blit_buffer(self.buffer, 0, 0, self.width, self.height)
