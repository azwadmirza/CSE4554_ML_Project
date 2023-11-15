    def get_shed_config_dict(self, app):
        """
        Return the in-memory version of the shed_tool_conf file, which is stored in the config_elems entry
        in the shed_tool_conf_dict.
        """

        def _is_valid_shed_config_filename(filename):
            for shed_tool_conf_dict in app.toolbox.dynamic_confs(include_migrated_tool_conf=True):
                if filename == shed_tool_conf_dict['config_filename']:
                    return True
            return False

        if not self.shed_config_filename or not _is_valid_shed_config_filename(self.shed_config_filename):
            return self.guess_shed_config(app)
        for shed_tool_conf_dict in app.toolbox.dynamic_confs(include_migrated_tool_conf=True):
            if self.shed_config_filename == shed_tool_conf_dict['config_filename']:
                return shed_tool_conf_dict
        return {}