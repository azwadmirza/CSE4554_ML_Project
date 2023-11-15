    def run_cell(self):
        """Run current cell."""
        text, block = self.get_current_editor().get_cell_as_executable_code()
        self._run_cell_text(text, block)