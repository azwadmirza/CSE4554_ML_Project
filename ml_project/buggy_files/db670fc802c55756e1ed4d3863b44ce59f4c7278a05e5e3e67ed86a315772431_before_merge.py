    def active(self):
        """Get the name of the active virtual environment.

        You can use this as a key to get further information.

        Returns None if no environment is active.
        """
        if "VIRTUAL_ENV" not in builtins.__xonsh__.env:
            return
        env_path = builtins.__xonsh__.env["VIRTUAL_ENV"]
        if env_path.startswith(self.venvdir):
            name = env_path[len(self.venvdir) :]
            if name[0] in "/\\":
                name = name[1:]
            return name
        else:
            return env_path