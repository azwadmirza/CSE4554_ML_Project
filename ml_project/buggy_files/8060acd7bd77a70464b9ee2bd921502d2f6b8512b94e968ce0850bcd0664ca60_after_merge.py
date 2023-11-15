    def run_cell(self, debug=False):
        """Run current cell."""
        text, block = self.get_current_editor().get_cell_as_executable_code()
        finfo = self.get_current_finfo()
        editor = self.get_current_editor()
        cell_name = self._get_cell_name(block)
        filename = finfo.filename

        self._run_cell_text(text, editor, (filename, cell_name), debug)