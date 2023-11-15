    def create_lineedit(self, text, option, default=NoDefault,
                        tip=None, alignment=Qt.Vertical, regex=None, 
                        restart=False, word_wrap=True, placeholder=None):
        label = QLabel(text)
        label.setWordWrap(word_wrap)
        edit = QLineEdit()
        layout = QVBoxLayout() if alignment == Qt.Vertical else QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(edit)
        layout.setContentsMargins(0, 0, 0, 0)
        if tip:
            edit.setToolTip(tip)
        if regex:
            edit.setValidator(QRegExpValidator(QRegExp(regex)))
        if placeholder:
            edit.setPlaceholderText(placeholder)
        self.lineedits[edit] = (option, default)
        widget = QWidget(self)
        widget.label = label
        widget.textbox = edit
        widget.setLayout(layout)
        edit.restart_required = restart
        edit.label_text = text
        return widget