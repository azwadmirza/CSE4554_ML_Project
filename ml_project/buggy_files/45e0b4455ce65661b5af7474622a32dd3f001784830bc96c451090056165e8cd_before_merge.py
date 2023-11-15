    def data(self, index, role=Qt.DisplayRole):
        """Cell content"""
        if not index.isValid():
            return to_qvariant()
        value = self.get_value(index)
        if is_binary_string(value):
            try:
                value = to_text_string(value, 'utf8')
            except:
                pass
        if role == Qt.DisplayRole:
            if value is np.ma.masked:
                return ''
            else:
                try:
                    return to_qvariant(self._format % value)
                except TypeError:
                    self.readonly = True
                    return repr(value)
        elif role == Qt.TextAlignmentRole:
            return to_qvariant(int(Qt.AlignCenter|Qt.AlignVCenter))
        elif role == Qt.BackgroundColorRole and self.bgcolor_enabled \
          and value is not np.ma.masked:
            try:
                hue = (self.hue0 +
                       self.dhue * (float(self.vmax) - self.color_func(value))
                       / (float(self.vmax) - self.vmin))
                hue = float(np.abs(hue))
                color = QColor.fromHsvF(hue, self.sat, self.val, self.alp)
                return to_qvariant(color)
            except TypeError:
                return to_qvariant()
        elif role == Qt.FontRole:
            return to_qvariant(get_font(font_size_delta=DEFAULT_SMALL_DELTA))
        return to_qvariant()