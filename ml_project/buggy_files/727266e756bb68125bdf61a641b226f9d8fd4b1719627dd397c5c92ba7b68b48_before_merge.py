    def activate(self, name):
        """
        Activate a virtual environment.

        Parameters
        ----------
        name : str
            Virtual environment name or absolute path.
        """
        env = builtins.__xonsh__.env
        ve = self[name]
        if "VIRTUAL_ENV" in env:
            self.deactivate()

        type(self).oldvars = {"PATH": list(env["PATH"])}
        env["PATH"].insert(0, ve.bin)
        env["VIRTUAL_ENV"] = ve.env
        if "PYTHONHOME" in env:
            type(self).oldvars["PYTHONHOME"] = env.pop("PYTHONHOME")

        events.vox_on_activate.fire(name=name, path=ve.env)