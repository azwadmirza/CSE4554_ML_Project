    def draw(self, x, y, bar_height=None, rounded=True, fill=False,
             line=False):
        self.drawer.set_source_rgb(self.border_color)
        opts = [
            x, y,
            self.layout.width + self.pad_left + self.pad_right,
            self.layout.height + self.pad_top + self.pad_bottom,
            self.border_width
        ]
        if line:
            if not bar_height:
                bar_height = self.layout.height + self.pad_top + self.pad_bottom
            highlight_opts = [
                x, 0,
                self.layout.width + self.pad_left + self.pad_right,
                bar_height,
                self.border_width
            ]
            self.drawer.set_source_rgb(self.highlight_color)
            self.drawer.fillrect(*highlight_opts)

            lineopts = [
                x,
                bar_height - self.line_thickness,
                self.layout.width + self.pad_left + self.pad_right,
                self.line_thickness,
                self.border_width
            ]

            self.drawer.set_source_rgb(self.border_color)
            self.drawer.fillrect(*lineopts)
        elif fill:
            if rounded:
                self.drawer.rounded_fillrect(*opts)
            else:
                self.drawer.fillrect(*opts)
        else:
            if rounded:
                self.drawer.rounded_rectangle(*opts)
            else:
                self.drawer.rectangle(*opts)
        self.drawer.ctx.stroke()
        self.layout.draw(
            x + self.pad_left,
            y + self.pad_top
        )