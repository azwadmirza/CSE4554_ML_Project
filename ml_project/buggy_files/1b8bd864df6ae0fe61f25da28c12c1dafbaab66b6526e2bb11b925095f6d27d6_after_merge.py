    def drawbox(self, offset, text, bordercolor, textcolor,
                width=None, rounded=False, block=False, line=False, highlighted=False):
        self.layout.text = text
        self.layout.font_family = self.font
        self.layout.font_size = self.fontsize
        self.layout.colour = textcolor
        if width is not None:
            self.layout.width = width
        if line:
            pad_y = (self.bar.height - self.layout.height) / 2
        else:
            pad_y = self.padding_y
        framed = self.layout.framed(
            self.borderwidth,
            bordercolor,
            self.padding_x,
            pad_y,
            self.highlight_color
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
            framed.draw_line(offset, y, highlighted)
        else:
            framed.draw(offset, y, rounded)