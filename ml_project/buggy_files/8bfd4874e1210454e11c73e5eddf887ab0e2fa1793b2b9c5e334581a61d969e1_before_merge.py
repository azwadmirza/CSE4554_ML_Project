    def _send_string_selection(self, string: str):
        """Use the mouse selection clipboard to send a string."""
        backup = self.clipboard.selection  # Keep a backup of current content, to restore the original afterwards.
        self.clipboard.selection = string
        self.__enqueue(self._paste_using_mouse_button_2)
        self.__enqueue(self._restore_clipboard_selection, backup)