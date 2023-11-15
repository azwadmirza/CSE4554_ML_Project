    def _glyph_properties(self, *args):
        props = super(BarPlot, self)._glyph_properties(*args)
        del props['width']
        return props