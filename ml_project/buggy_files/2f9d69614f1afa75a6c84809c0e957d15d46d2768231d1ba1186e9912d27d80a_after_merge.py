    def createEditor(self, parent, option, index):
        """Create editor widget"""
        model = index.model()
        value = model.get_value(index)
        if type(value) == np.ndarray or model.readonly:
            # The editor currently cannot properly handle this case
            return
        elif model._data.dtype.name == "bool":
            value = not value
            model.setData(index, to_qvariant(value))
            return
        elif value is not np.ma.masked:
            editor = QLineEdit(parent)
            editor.setFont(get_font(font_size_delta=DEFAULT_SMALL_DELTA))
            editor.setAlignment(Qt.AlignCenter)
            if is_number(self.dtype):
                validator = QDoubleValidator(editor)
                validator.setLocale(QLocale('C'))
                editor.setValidator(validator)
            editor.returnPressed.connect(self.commitAndCloseEditor)
            return editor