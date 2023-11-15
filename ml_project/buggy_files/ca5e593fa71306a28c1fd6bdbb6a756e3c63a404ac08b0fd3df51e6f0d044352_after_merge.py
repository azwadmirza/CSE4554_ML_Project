    def jedi_script(self, position=None):
        extra_paths = []
        environment_path = None
        env_vars = None

        if self._config:
            jedi_settings = self._config.plugin_settings('jedi', document_path=self.path)
            environment_path = jedi_settings.get('environment')
            extra_paths = jedi_settings.get('extra_paths') or []
            env_vars = jedi_settings.get('env_vars')

        # Drop PYTHONPATH from env_vars before creating the environment because that makes
        # Jedi throw an error.
        if env_vars is None:
            env_vars = os.environ.copy()
        env_vars.pop('PYTHONPATH', None)

        environment = self.get_enviroment(environment_path, env_vars=env_vars) if environment_path else None
        sys_path = self.sys_path(environment_path, env_vars=env_vars) + extra_paths
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