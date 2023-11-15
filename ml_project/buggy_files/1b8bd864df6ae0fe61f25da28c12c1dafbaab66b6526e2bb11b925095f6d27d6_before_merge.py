    def drawbox(self, offset, text, bordercolor, textcolor, highlight_color,
                line_thickness, rounded=False, block=False, width=None,
                line=False):
        self.layout.text = text
        self.layout.font_family = self.font
        self.layout.font_size = self.fontsize
        self.layout.colour = textcolor
        if width is not None:
            self.layout.width = width
        framed = self.layout.framed(
            self.borderwidth,
            bordercolor,
            self.padding_x,
            self.padding_y,
            highlight_color,
            line_thickness
        )
        y = self.margin_y
        if self.center_aligned:
            for t in base.MarginMixin.defaults:
                if t[0] == 'margin':
                    y += (self.bar.height - framed.height) / 2 - t[1]
                    break
        if block:
            framed.draw_fill(offset, y, rounded)
        elif line:
            framed.draw_line(offset, y, self.bar.size, rounded)
        else:
            framed.draw(offset, y, rounded)