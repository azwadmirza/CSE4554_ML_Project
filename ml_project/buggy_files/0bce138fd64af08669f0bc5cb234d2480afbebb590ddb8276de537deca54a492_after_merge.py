    def directory_select(self, message, **unused_kwargs):
        """Display a directory selection screen.

        :param str message: prompt to give the user

        :returns: tuple of the form (`code`, `string`) where
            `code` - display exit code
            `string` - input entered by the user

        """
        root_directory = os.path.abspath(os.sep)
        return self.dialog.dselect(
            filepath=root_directory, help_button=True, title=message)