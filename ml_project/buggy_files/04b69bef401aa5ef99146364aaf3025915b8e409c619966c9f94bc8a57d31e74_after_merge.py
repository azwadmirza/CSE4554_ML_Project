    def _glyph_properties(self, *args):
        props = super(BarPlot, self)._glyph_properties(*args)
        return {k: v for k, v in props.items() if k not in ['width', 'bar_width']}