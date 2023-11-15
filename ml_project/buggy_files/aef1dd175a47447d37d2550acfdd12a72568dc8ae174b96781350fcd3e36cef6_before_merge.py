    def reset_status(self):
        """Reset self._new_tool_ids and self._removed_tool_ids once
        all operations that need to know about new tools have finished running."""
        self._new_tool_ids = set()
        self._removed_tool_ids = set()