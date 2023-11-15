    def set_pattern(self, val):
        """Setter for pattern.

        Args:
            val: The value to set.
        """
        self._pattern = val
        val = re.sub(r' +', r' ', val)  # See #1919
        val = re.escape(val)
        val = val.replace(r'\ ', '.*')
        rx = QRegularExpression(val, QRegularExpression.CaseInsensitiveOption)
        qtutils.ensure_valid(rx)
        self.setFilterRegularExpression(rx)
        self.invalidate()
        sortcol = 0
        self.sort(sortcol)