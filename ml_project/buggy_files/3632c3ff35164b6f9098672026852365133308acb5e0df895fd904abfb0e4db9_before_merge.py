    def get_enviroment(self, environment_path=None):
        # TODO(gatesn): #339 - make better use of jedi environments, they seem pretty powerful
        if environment_path is None:
            environment = jedi.api.environment.get_cached_default_environment()
        else:
            if environment_path in self._workspace._environments:
                environment = self._workspace._environments[environment_path]
            else:
                environment = jedi.api.environment.create_environment(path=environment_path, safe=False)
                self._workspace._environments[environment_path] = environment

        return environment