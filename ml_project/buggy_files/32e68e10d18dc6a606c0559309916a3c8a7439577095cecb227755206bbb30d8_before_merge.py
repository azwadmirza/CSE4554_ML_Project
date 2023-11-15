    def go_to_error(self, text):
        """Go to error if relevant"""
        match = get_error_match(to_text_string(text))
        if match:
            fname, lnb = match.groups()
            if ("<ipython-input-" in fname and
                    self.run_cell_filename is not None):
                fname = self.run_cell_filename
            self.edit_goto.emit(osp.abspath(fname), int(lnb), '')