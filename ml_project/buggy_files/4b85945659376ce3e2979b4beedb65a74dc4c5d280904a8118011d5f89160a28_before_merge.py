    def show_in_external_file_explorer(self, fnames=None):
        """Show file in external file explorer"""
        if fnames is None:
            fnames = self.get_current_filename()
        show_in_external_file_explorer(fnames)