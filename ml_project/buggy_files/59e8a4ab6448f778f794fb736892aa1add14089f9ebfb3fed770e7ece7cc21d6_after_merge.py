    def cleanup(self):
        """
        Remove uninstalled tools from tool cache if they are not on disk anymore or if their content has changed.

        Returns list of tool_ids that have been removed.
        """
        removed_tool_ids = []
        try:
            paths_to_cleanup = {path: tool.all_ids for path, tool in self._tools_by_path.items() if self._should_cleanup(path)}
            for config_filename, tool_ids in paths_to_cleanup.items():
                del self._hash_by_tool_paths[config_filename]
                if os.path.exists(config_filename):
                    # This tool has probably been broken while editing on disk
                    # We record it here, so that we can recover it
                    self._removed_tools_by_path[config_filename] = self._tools_by_path[config_filename]
                del self._tools_by_path[config_filename]
                for tool_id in tool_ids:
                    if tool_id in self._tool_paths_by_id:
                        del self._tool_paths_by_id[tool_id]
                removed_tool_ids.extend(tool_ids)
            for tool_id in removed_tool_ids:
                self._removed_tool_ids.add(tool_id)
                if tool_id in self._new_tool_ids:
                    self._new_tool_ids.remove(tool_id)
        except Exception:
            # If by chance the file is being removed while calculating the hash or modtime
            # we don't want the thread to die.
            pass
        return removed_tool_ids