    def _run_cell_text(self, text, block):
        """Run cell code in the console.

        Cell code is run in the console by copying it to the console if
        `self.run_cell_copy` is ``True`` otherwise by using the `run_cell`
        function.

        Parameters
        ----------
        text : str
            The code in the cell as a string.
        line : int
            The starting line number of the cell in the file.
        """
        finfo = self.get_current_finfo()
        editor = self.get_current_editor()
        cell_name = self._get_cell_name(block)
        if finfo.editor.is_python() and text:
            self.run_cell_in_ipyclient.emit(text, cell_name,
                                            finfo.filename,
                                            self.run_cell_copy)
        editor.setFocus()