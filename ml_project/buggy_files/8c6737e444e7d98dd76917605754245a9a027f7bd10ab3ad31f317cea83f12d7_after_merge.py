    def checklist(self, message, tags, default_status=True, **unused_kwargs):
        """Displays a checklist.

        :param message: Message to display before choices
        :param list tags: where each is of type :class:`str` len(tags) > 0
        :param bool default_status: If True, items are in a selected state by
            default.
        :param dict _kwargs: absorbs default / cli_args


        :returns: tuple of the form (`code`, `list_tags`) where
            `code` - display exit code
            `list_tags` - list of str tags selected by the user

        """
        choices = [(tag, "", default_status) for tag in tags]
        return self.dialog.checklist(message, choices=choices)