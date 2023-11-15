    def edit(self, text, caret_position=None):
        """Edit a given text.

        Args:
            text: The initial text to edit.
            caret_position: The position of the caret in the text.
        """
        if self._filename is not None:
            raise ValueError("Already editing a file!")
        try:
            self._filename = self._create_tempfile(text, 'qutebrowser-editor-')
        except OSError as e:
            message.error("Failed to create initial file: {}".format(e))
            return

        self._remove_file = True

        line, column = self._calc_line_and_column(text, caret_position)
        self._start_editor(line=line, column=column)