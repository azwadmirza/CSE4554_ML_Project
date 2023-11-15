    def relocate(self, dirpath):
        """Relocate sets up variables for, eg, the expected location and name of
        the Python and Pip binaries, but doesn't access the file system. That's
        done by code in or called from `create`
        """
        self.path = str(dirpath)
        self.name = os.path.basename(self.path)
        self._bin_directory = os.path.join(
            self.path, "scripts" if self._is_windows else "bin"
        )
        #
        # Pip and the interpreter will be set up when the virtualenv is created
        #
        self.interpreter = os.path.join(
            self._bin_directory, "python" + self._bin_extension
        )
        self.pip = Pip(
            os.path.join(self._bin_directory, "pip" + self._bin_extension)
        )
        logger.debug(
            "Virtual environment set up %s at %s", self.name, self.path
        )
        self.settings["dirpath"] = self.path