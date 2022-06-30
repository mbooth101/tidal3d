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

    def chequerboard(self, size, dark_colour, light_colour):
        """
        Draws a chequerboard pattern to the framebuffer with squares of the given size and alternating
        colours
        """
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

    def pixel(self, p, colour):
        """
        Set a pixel in the framebuffer at the given coords to the given colour
        """
        self.fb.pixel(int(p[0]), int(p[1]), colour)

    def triangle(self, p1, p2, p3, colour):
        """
        Draw a triangle on the framebuffer between the three given coords of the given colour
        """
        self.fb.line(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]), colour)
        self.fb.line(int(p2[0]), int(p2[1]), int(p3[0]), int(p3[1]), colour)
        self.fb.line(int(p3[0]), int(p3[1]), int(p1[0]), int(p1[1]), colour)

    def blit(self):
        """
        Send the framebuffer to the display
        """
        self.display.blit_buffer(self.buffer, 0, 0, self.width, self.height)
