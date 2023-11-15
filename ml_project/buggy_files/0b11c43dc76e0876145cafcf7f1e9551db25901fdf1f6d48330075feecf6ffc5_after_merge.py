    def __init__(self, text, title='', font=None, parent=None,
                 readonly=False, size=(400, 300)):
        QDialog.__init__(self, parent)
        
        # Destroying the C++ object right after closing the dialog box,
        # otherwise it may be garbage-collected in another QThread
        # (e.g. the editor's analysis thread in Spyder), thus leading to
        # a segmentation fault on UNIX or an application crash on Windows
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.text = None
        self.btn_save_and_close = None
        
        # Display text as unicode if it comes as bytes, so users see 
        # its right representation
        if is_binary_string(text):
            self.is_binary = True
            text = to_text_string(text, 'utf8')
        else:
            self.is_binary = False
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Text edit
        self.edit = QTextEdit(parent)
        self.edit.setReadOnly(readonly)
        self.edit.textChanged.connect(self.text_changed)
        self.edit.setPlainText(text)
        if font is None:
            font = get_font()
        self.edit.setFont(font)
        self.layout.addWidget(self.edit)

        # Buttons configuration
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        if not readonly:
            self.btn_save_and_close = QPushButton(_('Save and Close'))
            self.btn_save_and_close.setDisabled(True)
            self.btn_save_and_close.clicked.connect(self.accept)
            btn_layout.addWidget(self.btn_save_and_close)

        self.btn_close = QPushButton(_('Close'))
        self.btn_close.setAutoDefault(True)
        self.btn_close.setDefault(True)
        self.btn_close.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_close)

        self.layout.addLayout(btn_layout)

        # Make the dialog act as a window
        self.setWindowFlags(Qt.Window)
        
        self.setWindowIcon(ima.icon('edit'))
        if title:
            try:
                unicode_title = to_text_string(title)
            except UnicodeEncodeError:
                unicode_title = u''
        else:
            unicode_title = u''

        self.setWindowTitle(_("Text editor") + \
                            u"%s" % (u" - " + unicode_title
                                     if unicode_title else u""))
        self.resize(size[0], size[1])