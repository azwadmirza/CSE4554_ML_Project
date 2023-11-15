    def find_text(self, text, changed=True,
                  forward=True, case=False, words=False,
                  regexp=False):
        """Find text"""
        if not WEBENGINE:
            findflag = QWebEnginePage.FindWrapsAroundDocument
        else:
            findflag = 0

        if not forward:
            findflag = findflag | QWebEnginePage.FindBackward
        if case:
            findflag = findflag | QWebEnginePage.FindCaseSensitively

        return self.findText(text, QWebEnginePage.FindFlags(findflag))