    def directory_select(self, message, **unused_kwargs):
        """Display a directory selection screen.

        :param str message: prompt to give the user

        :returns: tuple of the form (`code`, `string`) where
            `code` - display exit code
            `string` - input entered by the user

        """
        root_directory = os.path.abspath(os.sep)
        return _clean(self.dialog.dselect(
            filepath=root_directory, width=self.width,
            height=self.height, help_button=True, title=message))