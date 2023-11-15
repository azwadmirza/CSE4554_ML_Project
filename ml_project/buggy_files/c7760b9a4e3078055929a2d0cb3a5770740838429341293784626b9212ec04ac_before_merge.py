    def edit(self, text, caret_position=None):
        """Edit a given text.

        Args:
            text: The initial text to edit.
            caret_position: The position of the caret in the text.
        """
        if self._filename is not None:
            raise ValueError("Already editing a file!")
        try:
            # Close while the external process is running, as otherwise systems
            # with exclusive write access (e.g. Windows) may fail to update
            # the file from the external editor, see
            # https://github.com/qutebrowser/qutebrowser/issues/1767
            with tempfile.NamedTemporaryFile(
                    # pylint: disable=bad-continuation
                    mode='w', prefix='qutebrowser-editor-',
                    encoding=config.val.editor.encoding,
                    delete=False) as fobj:
                    # pylint: enable=bad-continuation
                if text:
                    fobj.write(text)
                self._filename = fobj.name
        except OSError as e:
            message.error("Failed to create initial file: {}".format(e))
            return

        self._remove_file = True

        line, column = self._calc_line_and_column(text, caret_position)
        self._start_editor(line=line, column=column)