    def draw(self):
        self.drawer.clear(self.background or self.bar.background)
        offset = 0

        for w in self.bar.screen.group.windows:
            state = ''
            if w is None:
                pass
            elif w.maximized:
                state = '[] '
            elif w.minimized:
                state = '_ '
            elif w.floating:
                state = 'V '
            task = "%s%s" % (state, w.name if w and w.name else " ")

            if w.urgent:
                border = self.urgent_border
            elif w is w.group.currentWindow:
                border = self.border
            else:
                border = self.background or self.bar.background

            bw = self.box_width(task)
            self.drawbox(
                self.margin_x + offset,
                task,
                border,
                self.foreground,
                rounded=self.rounded,
                block=(self.highlight_method == 'block'),
                width=(bw - self.margin_x * 2 - self.padding_x * 2),
                icon=self.get_window_icon(w),
            )

            offset += bw + self.icon_size
        self.drawer.draw(offsetx=self.offset, width=self.width)