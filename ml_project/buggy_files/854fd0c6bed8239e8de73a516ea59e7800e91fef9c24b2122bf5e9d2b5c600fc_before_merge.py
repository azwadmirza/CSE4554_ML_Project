    def find_text(self, text, changed=True,
                  forward=True, case=False, words=False,
                  regexp=False):
        """Find text"""
        findflag = QWebEnginePage.FindWrapsAroundDocument
        if not forward:
            findflag = findflag | QWebEnginePage.FindBackward
        if case:
            findflag = findflag | QWebEnginePage.FindCaseSensitively
        return self.findText(text, findflag)