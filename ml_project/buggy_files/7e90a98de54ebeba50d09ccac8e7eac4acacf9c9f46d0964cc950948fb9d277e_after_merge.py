    def _run_cell_text(self, text, editor, cell_id, debug=False):
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
        (filename, cell_name) = cell_id
        if editor.is_python() and text:
            args = (text, cell_name, filename, self.run_cell_copy)
            if debug:
                self.debug_cell_in_ipyclient.emit(*args)
            else:
                self.run_cell_in_ipyclient.emit(*args)
        editor.setFocus()