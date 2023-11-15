    def reset_status(self):
        """
        Reset tracking of new and newly disabled tools.
        """
        self._new_tool_ids = set()
        self._removed_tool_ids = set()
        self._removed_tools_by_path = {}