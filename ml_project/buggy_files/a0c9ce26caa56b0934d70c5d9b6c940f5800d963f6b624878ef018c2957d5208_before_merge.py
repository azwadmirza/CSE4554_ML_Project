    def get_selection_first_block(self):
        """Return the first block of the selection."""
        cursor = self.textCursor()
        start, end = cursor.selectionStart(), cursor.selectionEnd()
        if start > 0:
            start = start - 1
        return self.document().findBlock(start)