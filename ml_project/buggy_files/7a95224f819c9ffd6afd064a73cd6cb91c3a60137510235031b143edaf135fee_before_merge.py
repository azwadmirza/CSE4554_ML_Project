    def framed(self, border_width, border_color, pad_x, pad_y,
               highlight_color=None, line_thickness=None):
        return TextFrame(self, border_width, border_color, pad_x, pad_y,
                         highlight_color, line_thickness)