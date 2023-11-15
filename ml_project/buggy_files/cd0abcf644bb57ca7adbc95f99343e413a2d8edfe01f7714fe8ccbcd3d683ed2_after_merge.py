    def re_run_last_cell(self):
        """Run the previous cell again."""
        if self.last_cell_call is None:
            return
        filename, cell_name = self.last_cell_call
        index = self.has_filename(filename)
        if index is None:
            return
        editor = self.data[index].editor

        try:
            text = editor.get_cell_code(cell_name)
        except RuntimeError:
            return

        self._run_cell_text(text, editor, (filename, cell_name))