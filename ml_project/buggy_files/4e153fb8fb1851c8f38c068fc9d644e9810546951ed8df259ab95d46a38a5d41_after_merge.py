    def setData(self, index, value, role=Qt.EditRole):
        """Cell content change"""
        if not index.isValid() or self.readonly:
            return False
        i = index.row()
        j = index.column()
        value = from_qvariant(value, str)
        dtype = self._data.dtype.name
        if dtype == "bool":
            try:
                val = bool(float(value))
            except ValueError:
                val = value.lower() == "true"
        elif dtype.startswith("string") or dtype.startswith("bytes"):
            val = to_binary_string(value, 'utf8')
        elif dtype.startswith("unicode") or dtype.startswith("str"):
            val = to_text_string(value)
        else:
            if value.lower().startswith('e') or value.lower().endswith('e'):
                return False
            try:
                val = complex(value)
                if not val.imag:
                    val = val.real
            except ValueError as e:
                QMessageBox.critical(self.dialog, "Error",
                                     "Value error: %s" % str(e))
                return False
        try:
            self.test_array[0] = val  # will raise an Exception eventually
        except OverflowError as e:
            print("OverflowError: " + str(e))  # spyder: test-skip
            QMessageBox.critical(self.dialog, "Error",
                                 "Overflow error: %s" % str(e))
            return False

        # Add change to self.changes
        self.changes[(i, j)] = val
        self.dataChanged.emit(index, index)

        if not is_string(val):
            val = self.color_func(val)

            if val > self.vmax:
                self.vmax = val

            if val < self.vmin:
                self.vmin = val

        return True