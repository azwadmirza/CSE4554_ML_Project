    def __init__(self, pos, color, mode=None):
        """
        ===============     ==============================================================
        **Arguments:**
        pos                 Array of positions where each color is defined
        color               Array of RGBA colors.
                            Integer data types are interpreted as 0-255; float data types
                            are interpreted as 0.0-1.0
        mode                Array of color modes (ColorMap.RGB, HSV_POS, or HSV_NEG)
                            indicating the color space that should be used when
                            interpolating between stops. Note that the last mode value is
                            ignored. By default, the mode is entirely RGB.
        ===============     ==============================================================
        """
        self.pos = np.array(pos)
        order = np.argsort(self.pos)
        self.pos = self.pos[order]
        self.color = np.array(color)[order]
        if mode is None:
            mode = np.ones(len(pos))
        self.mode = mode
        self.stopsCache = {}