    def highlightBlock(self, text):
        """
        Highlights a block of text. Please do not override, this method.
        Instead you should implement
        :func:`spyder.utils.syntaxhighplighters.SyntaxHighlighter.highlight_block`.

        :param text: text to highlight.
        """
        self.highlight_block(text)
        if self.request_folding:
            if self.editor is not None:
                if self.editor.folding_supported and self.editor.code_folding:
                    diff, _ = self.editor.text_diff
                    if len(diff) > 0:
                        self.editor.request_folding()