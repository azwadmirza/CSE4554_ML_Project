    def set_pattern(self, val):
        """Setter for pattern.

        Args:
            val: The value to set.
        """
        if len(val) > 5000:  # avoid crash on huge search terms (#5973)
            log.completion.warning(f"Trimming {len(val)}-char pattern to 5000")
            val = val[:5000]
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