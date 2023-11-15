    def __init__(self, x, y, values, column=None, stat='count', glyph='rect', width=1,
                 height=1, **kwargs):
        kwargs['x'] = x
        kwargs['y'] = y
        kwargs['values'] = values
        kwargs['column'] = column
        kwargs['stat'] = stat
        kwargs['glyph_name'] = glyph
        kwargs['height'] = height
        kwargs['width'] = width
        super(XyGlyph, self).__init__(**kwargs)
        self.setup()