    def _send_string_clipboard(self, string: str, paste_command: model.SendMode):
        """Use the clipboard to send a string.
        """
        backup = self.clipboard.text  # Keep a backup of current content, to restore the original afterwards.
        self.clipboard.text = string
        self.mediator.send_string(paste_command.value)
        # Because send_string is queued, also enqueue the clipboard restore, to keep the proper action ordering.
        self.__enqueue(self._restore_clipboard_text, backup)