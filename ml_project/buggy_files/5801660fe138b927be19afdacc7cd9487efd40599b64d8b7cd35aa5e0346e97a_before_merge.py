    def __init__(self, parent, lexer=None):
        super(PygmentsHighlighter, self).__init__(parent)

        self._document = QtGui.QTextDocument()
        self._formatter = HtmlFormatter(nowrap=True)
        self._lexer = lexer if lexer else PythonLexer()
        self.set_style('default')