    def input(self, message, **unused_kwargs):
        """Display an input box to the user.

        :param str message: Message to display that asks for input.
        :param dict _kwargs: absorbs default / cli_args

        :returns: tuple of the form (`code`, `string`) where
            `code` - display exit code
            `string` - input entered by the user

        """
        return self.dialog.inputbox(message)