    def _restore_clipboard_text(self, backup: str):
        """Restore the clipboard content."""
        # Pasting takes some time, so wait a bit before restoring the content. Otherwise the restore is done before
        # the pasting happens, causing the backup to be pasted instead of the desired clipboard content.
        time.sleep(0.2)
        self.clipboard.text = backup if backup is not None else ""