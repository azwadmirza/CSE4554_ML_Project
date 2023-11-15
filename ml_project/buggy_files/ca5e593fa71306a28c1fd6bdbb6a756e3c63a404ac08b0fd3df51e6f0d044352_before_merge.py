    def jedi_script(self, position=None):
        extra_paths = []
        environment_path = None

        if self._config:
            jedi_settings = self._config.plugin_settings('jedi', document_path=self.path)
            environment_path = jedi_settings.get('environment')
            extra_paths = jedi_settings.get('extra_paths') or []

        environment = self.get_enviroment(environment_path) if environment_path else None
        sys_path = self.sys_path(environment_path) + extra_paths
        project_path = self._workspace.root_path

        kwargs = {
            'code': self.source,
            'path': self.path,
            'environment': environment,
            'project': jedi.Project(path=project_path, sys_path=sys_path),
        }

        if position:
            # Deprecated by Jedi to use in Script() constructor
            kwargs += _utils.position_to_jedi_linecolumn(self, position)

        return jedi.Script(**kwargs)