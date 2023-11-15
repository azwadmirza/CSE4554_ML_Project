    def sys_path(self, environment_path=None):
        # Copy our extra sys path
        path = list(self._extra_sys_path)
        environment = self.get_enviroment(environment_path=environment_path)
        path.extend(environment.get_sys_path())
        return path