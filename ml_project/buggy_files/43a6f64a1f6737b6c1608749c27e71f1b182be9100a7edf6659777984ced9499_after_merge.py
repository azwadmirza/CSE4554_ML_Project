    def ensure_interpreter(self):
        """Ensure there is an interpreter of the expected name at the expected
        location, given the platform and naming conventions

        NB if the interpreter is present as a symlink to a system interpreter (likely
        for a venv) but the link is broken, then os.path.isfile will fail as though
        the file wasn't there. Which is what we want in these circumstances
        """
        if os.path.isfile(self.interpreter):
            logger.info("Interpreter found at %s", self.interpreter)
        else:
            message = (
                "Interpreter not found where expected at %s" % self.interpreter
            )
            logger.error(message)
            raise VirtualEnvironmentError(message)