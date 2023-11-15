    def yesno(self, message, yes_label="Yes", no_label="No", **unused_kwargs):
        """Display a Yes/No dialog box.

        Yes and No label must begin with different letters.

        :param str message: message to display to user
        :param str yes_label: label on the "yes" button
        :param str no_label: label on the "no" button
        :param dict _kwargs: absorbs default / cli_args

        :returns: if yes_label was selected
        :rtype: bool

        """
        return self.dialog.DIALOG_OK == self.dialog.yesno(
            message, yes_label=yes_label, no_label=no_label)