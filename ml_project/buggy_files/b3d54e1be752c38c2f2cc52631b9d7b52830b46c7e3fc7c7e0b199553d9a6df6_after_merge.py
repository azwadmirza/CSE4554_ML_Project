    def highlightBlock(self, text):
        """
        Highlights a block of text. Please do not override, this method.
        Instead you should implement
        :func:`spyder.utils.syntaxhighplighters.SyntaxHighlighter.highlight_block`.

        :param text: text to highlight.
        """
        self.highlight_block(text)