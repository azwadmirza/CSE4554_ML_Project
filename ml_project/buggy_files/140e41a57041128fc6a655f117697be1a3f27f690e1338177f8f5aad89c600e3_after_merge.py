    def sys_path(self, environment_path=None, env_vars=None):
        # Copy our extra sys path
        # TODO: when safe to break API, use env_vars explicitly to pass to create_environment
        path = list(self._extra_sys_path)
        environment = self.get_enviroment(environment_path=environment_path, env_vars=env_vars)
        path.extend(environment.get_sys_path())
        return path