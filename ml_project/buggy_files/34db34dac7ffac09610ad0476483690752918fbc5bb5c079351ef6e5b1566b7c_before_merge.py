    def get_selected_text(self):
        """
        Return text selected by current text cursor, converted in unicode

        Replace the unicode line separator character \u2029 by
        the line separator characters returned by get_line_separator
        """
        return to_text_string(self.textCursor().selectedText()).replace(u"\u2029",
                                                     self.get_line_separator())