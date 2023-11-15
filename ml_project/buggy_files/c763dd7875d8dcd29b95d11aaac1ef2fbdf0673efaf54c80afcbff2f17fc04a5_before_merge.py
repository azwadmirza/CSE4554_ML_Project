    def input(self, message, **unused_kwargs):
        """Display an input box to the user.

        :param str message: Message to display that asks for input.
        :param dict _kwargs: absorbs default / cli_args

        :returns: tuple of the form (`code`, `string`) where
            `code` - display exit code
            `string` - input entered by the user

        """
        sections = message.split("\n")
        # each section takes at least one line, plus extras if it's longer than self.width
        wordlines = [1 + (len(section) / self.width) for section in sections]
        height = 6 + sum(wordlines) + len(sections)
        return _clean(self.dialog.inputbox(message, width=self.width, height=height))