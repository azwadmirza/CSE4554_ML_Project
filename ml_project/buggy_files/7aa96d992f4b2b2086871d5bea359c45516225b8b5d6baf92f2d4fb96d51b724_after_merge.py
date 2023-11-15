    def go_to_error(self, text):
        """Go to error if relevant"""
        match = get_error_match(to_text_string(text))
        if match:
            fname, lnb = match.groups()
            # This is needed to fix issue spyder-ide/spyder#9217
            try:
                self.edit_goto.emit(osp.abspath(fname), int(lnb), '')
            except ValueError:
                pass