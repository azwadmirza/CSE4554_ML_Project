    def get_repository_tools_tups(self):
        """
        Return a list of tuples of the form (relative_path, guid, tool) for each tool defined
        in the received tool shed repository metadata.
        """
        repository_tools_tups = []
        shed_conf_dict = self.tpm.get_shed_tool_conf_dict(self.metadata_dict.get('shed_config_filename'))
        if 'tools' in self.metadata_dict:
            for tool_dict in self.metadata_dict['tools']:
                load_relative_path = relative_path = tool_dict.get('tool_config', None)
                if shed_conf_dict.get('tool_path'):
                    load_relative_path = os.path.join(shed_conf_dict.get('tool_path'), relative_path)
                guid = tool_dict.get('guid', None)
                if relative_path and guid:
                    try:
                        tool = self.app.toolbox.load_tool(os.path.abspath(load_relative_path), guid=guid, use_cached=False)
                    except Exception:
                        log.exception("Error while loading tool at path '%s'", load_relative_path)
                        tool = None
                else:
                    tool = None
                if tool:
                    repository_tools_tups.append((relative_path, guid, tool))
        return repository_tools_tups