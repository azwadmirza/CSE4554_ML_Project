    def __init__(self, connection, theme="day", parent=None):
        super().__init__(parent)
        self.connection = connection
        self.setFont(Font().load())
        self.setAcceptRichText(False)
        self.setReadOnly(False)
        self.setUndoRedoEnabled(False)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)
        # The following variable maintains the position where we know
        # the device cursor is placed. It is initialized to the beginning
        # of the QTextEdit (i.e. equal to the Qt cursor position)
        self.device_cursor_position = self.textCursor().position()
        self.setObjectName("replpane")
        self.set_theme(theme)
        self.unprocessed_input = b""  # used by process_bytes
        self.decoder = codecs.getincrementaldecoder("utf8")("replace")
        self.vt100_regex = re.compile(
            r"\x1B\[(?P<count>[\d]*)(;?[\d]*)*(?P<action>[A-Za-z])"
        )