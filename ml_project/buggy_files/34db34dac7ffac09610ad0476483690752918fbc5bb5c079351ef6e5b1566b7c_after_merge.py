    def get_selected_text(self, cursor=None):
        """
        Return text selected by current text cursor, converted in unicode.

        Replace the unicode line separator character \u2029 by
        the line separator characters returned by get_line_separator
        """
        if cursor is None:
            cursor = self.textCursor()
        return to_text_string(cursor.selectedText()).replace(u"\u2029",
                                                     self.get_line_separator())