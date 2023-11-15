    def get_selection_first_block(self, cursor=None):
        """Return the first block of the selection."""
        if cursor is None:
            cursor = self.textCursor()
        start = cursor.selectionStart()
        if start > 0:
            start = start - 1
        return self.document().findBlock(start)