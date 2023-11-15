    def get_bgcolor(self, index):
        """Background color depending on value."""
        column = index.column()
        if not self.bgcolor_enabled:
            return
        value = self.get_value(index.row(), column)
        if self.max_min_col[column] is None or isna(value):
            color = QColor(BACKGROUND_NONNUMBER_COLOR)
            if is_text_string(value):
                color.setAlphaF(BACKGROUND_STRING_ALPHA)
            else:
                color.setAlphaF(BACKGROUND_MISC_ALPHA)
        else:
            if isinstance(value, COMPLEX_NUMBER_TYPES):
                color_func = abs
            else:
                color_func = float
            vmax, vmin = self.return_max(self.max_min_col, column)
            if vmax - vmin == 0:
                vmax_vmin_diff = 1.0
            else:
                vmax_vmin_diff = vmax - vmin
            hue = (BACKGROUND_NUMBER_MINHUE + BACKGROUND_NUMBER_HUERANGE *
                   (vmax - color_func(value)) / (vmax_vmin_diff))
            hue = float(abs(hue))
            if hue > 1:
                hue = 1
            color = QColor.fromHsvF(hue, BACKGROUND_NUMBER_SATURATION,
                                    BACKGROUND_NUMBER_VALUE,
                                    BACKGROUND_NUMBER_ALPHA)
        return color