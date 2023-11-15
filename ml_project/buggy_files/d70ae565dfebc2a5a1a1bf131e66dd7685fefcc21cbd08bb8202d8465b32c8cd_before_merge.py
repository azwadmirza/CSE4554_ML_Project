    def __init__(self, layout, border_width, border_color, pad_x, pad_y,
                 highlight_color, line_thickness):
        self.layout = layout
        self.border_width = border_width
        self.border_color = border_color
        self.drawer = self.layout.drawer
        self.highlight_color = highlight_color
        self.line_thickness = line_thickness

        if isinstance(pad_x, collections.Iterable):
            self.pad_left = pad_x[0]
            self.pad_right = pad_x[1]
        else:
            self.pad_left = self.pad_right = pad_x

        if isinstance(pad_y, collections.Iterable):
            self.pad_top = pad_y[0]
            self.pad_bottom = pad_y[1]
        else:
            self.pad_top = self.pad_bottom = pad_y