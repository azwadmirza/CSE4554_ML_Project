    def deactivate(self):
        """
        Deactivate the active virtual environment. Returns its name.
        """
        env = builtins.__xonsh__.env
        if not env["VIRTUAL_ENV"]:
            raise NoEnvironmentActive("No environment currently active.")

        env_name = self.active()

        if hasattr(type(self), "oldvars"):
            for k, v in type(self).oldvars.items():
                env[k] = v
            del type(self).oldvars

        del env["VIRTUAL_ENV"]

        events.vox_on_deactivate.fire(name=env_name, path=self[env_name].env)
        return env_name