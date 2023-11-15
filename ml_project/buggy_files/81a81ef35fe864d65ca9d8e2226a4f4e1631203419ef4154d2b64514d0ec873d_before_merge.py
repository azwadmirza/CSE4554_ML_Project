    def notification(self, message, height=10, pause=False):
        # pylint: disable=unused-argument
        """Display a notification to the user and wait for user acceptance.

        .. todo:: It probably makes sense to use one of the transient message
            types for pause. It isn't straightforward how best to approach
            the matter though given the context of our messages.
            http://pythondialog.sourceforge.net/doc/widgets.html#displaying-transient-messages

        :param str message: Message to display
        :param int height: Height of the dialog box
        :param bool pause: Not applicable to NcursesDisplay

        """
        self.dialog.msgbox(message, height, width=self.width)