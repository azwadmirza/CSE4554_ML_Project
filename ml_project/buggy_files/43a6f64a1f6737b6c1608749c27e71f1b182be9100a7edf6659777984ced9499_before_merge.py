    def ensure_interpreter(self):
        if os.path.isfile(self.interpreter):
            logger.info("Interpreter found at %s", self.interpreter)
        else:
            message = (
                "Interpreter not found where expected at %s" % self.interpreter
            )
            logger.error(message)
            raise VirtualEnvironmentError(message)