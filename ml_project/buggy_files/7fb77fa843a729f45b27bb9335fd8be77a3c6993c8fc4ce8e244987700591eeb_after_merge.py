    def draw_waveform(self, cr, width, height, elapsed_color, remaining_color):
        line_width = CONFIG.line_width
        value_count = len(self._rms_vals)
        max_value = max(self._rms_vals)
        ratio_width = value_count / float(width)
        ratio_height = max_value / float(height) * 2
        half_height = height // 2
        cr.set_line_width(line_width)

        if line_width < 2:
            # Default AA looks bad (and dimmer) for all 1px shapes.
            cr.set_antialias(1)

        position_width = self.position * width
        hw = line_width / 2.0
        # Avoiding object lookups is slightly faster
        data = self._rms_vals
        for x in range(0, width, line_width):
            fg_color = (elapsed_color if x < position_width
                        else remaining_color)
            cr.set_source_rgba(*list(fg_color))

            # Basic anti-aliasing / oversampling
            u1 = max(0, int(floor((x - hw) * ratio_width)))
            u2 = min(int(ceil((x + hw) * ratio_width)), len(data))
            val = (sum(data[u1:u2]) / (ratio_height * (u2 - u1))
                   if u1 != u2 else 0.5)

            # Draw single line, ensuring 1px minimum
            cr.move_to(x, half_height - val)
            cr.line_to(x, ceil(half_height + val))
            cr.stroke()