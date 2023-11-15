    def re_run_last_cell(self):
        """Run the previous cell again."""
        last_cell = (self.get_current_editor()
                     .get_last_cell_as_executable_code())
        if not last_cell:
            return
        self._run_cell_text(*last_cell)