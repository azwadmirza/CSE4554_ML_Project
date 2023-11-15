    def rehighlight(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.request_folding = False
        QSyntaxHighlighter.rehighlight(self)
        self.request_folding = True
        QApplication.restoreOverrideCursor()