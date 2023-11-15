    def __init__(self, question, parent=None):
        super().__init__(question, parent)
        self._init_texts(question)
        self._init_key_label()

        self._lineedit = LineEdit(self)
        if question.default:
            self._lineedit.setText(question.default)
        self._lineedit.textEdited.connect(self._set_fileview_root)
        self._vbox.addWidget(self._lineedit)

        self.setFocusProxy(self._lineedit)

        self._init_fileview()
        self._set_fileview_root(question.default)

        if config.val.prompt.filebrowser:
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self._to_complete = ''