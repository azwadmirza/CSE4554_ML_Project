    def get_bgcolor(self, index):
        """Background color depending on value"""
        column = index.column()
        if column == 0:
            color = QColor(Qt.lightGray)
            color.setAlphaF(.8)
            return color
        if not self.bgcolor_enabled:
            return
        value = self.get_value(index.row(), column-1)
        if isinstance(value, _sup_com):
            color_func = abs
        else:
            color_func = float
        if isinstance(value, _sup_nr+_sup_com) and self.bgcolor_enabled:
            vmax, vmin = self.return_max(self.max_min_col, column-1)
            hue = self.hue0 + self.dhue*(vmax-color_func(value)) / (vmax-vmin)
            hue = float(abs(hue))
            if hue > 1:
                hue = 1
            color = QColor.fromHsvF(hue, self.sat, self.val, self.alp)
        elif is_text_string(value):
            color = QColor(Qt.lightGray)
            color.setAlphaF(.05)
        else:
            color = QColor(Qt.lightGray)
            color.setAlphaF(.3)
        return color