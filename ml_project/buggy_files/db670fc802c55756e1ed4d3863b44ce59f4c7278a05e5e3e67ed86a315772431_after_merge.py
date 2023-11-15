    def active(self):
        """Get the name of the active virtual environment.

        You can use this as a key to get further information.

        Returns None if no environment is active.
        """
        env = builtins.__xonsh__.env
        if not env["VIRTUAL_ENV"]:
            return
        env_path = env["VIRTUAL_ENV"]
        if env_path.startswith(self.venvdir):
            name = env_path[len(self.venvdir) :]
            if name[0] in "/\\":
                name = name[1:]
            return name
        else:
            return env_path