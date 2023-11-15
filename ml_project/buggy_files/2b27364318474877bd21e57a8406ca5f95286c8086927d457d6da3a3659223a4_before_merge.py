    def draw(self):
        self.drawer.clear(self.background or self.bar.background)

        offset = 0
        for i, g in enumerate(self.groups):
            is_block = (self.highlight_method == 'block')
            is_line = (self.highlight_method == 'line')
            if not is_line:
                highlight_color = None

            bw = self.box_width([g])

            if self.group_has_urgent(g) and self.urgent_alert_method == "text":
                text_color = self.urgent_text
            elif g.windows:
                text_color = self.active
            else:
                text_color = self.inactive

            if g.screen:
                if self.highlight_method == 'text':
                    border = self.bar.background
                    text_color = self.this_current_screen_border
                else:
                    if self.bar.screen.group.name == g.name:
                        if self.qtile.currentScreen == self.bar.screen:
                            border = self.this_current_screen_border
                            highlight_color = self.highlight_color
                        else:
                            border = self.this_screen_border
                            highlight_color = self.bar.background
                    else:
                        border = self.other_screen_border
            elif self.group_has_urgent(g) and \
                    self.urgent_alert_method in ('border', 'block'):
                border = self.urgent_border
                if self.urgent_alert_method == 'block':
                    is_block = True
            else:
                border = self.background or self.bar.background
                highlight_color = self.bar.background

            self.drawbox(
                self.margin_x + offset,
                g.name,
                border,
                text_color,
                highlight_color,
                self.line_thickness,
                self.rounded,
                is_block,
                bw - self.margin_x * 2 - self.padding_x * 2,
                is_line
            )
            offset += bw
        self.drawer.draw(offsetx=self.offset, width=self.width)