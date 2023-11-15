    def _restore_clipboard_selection(self, backup: str):
        """Restore the selection clipboard content."""
        # Pasting takes some time, so wait a bit before restoring the content. Otherwise the restore is done before
        # the pasting happens, causing the backup to be pasted instead of the desired clipboard content.

        # Programmatically pressing the middle mouse button seems VERY slow, so wait rather long.
        # It might be a good idea to make this delay configurable. There might be systems that need even longer.
        time.sleep(1)
        self.clipboard.selection = backup if backup is not None else ""