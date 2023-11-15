    def _call_registered(self):
        """Calls all registered functions"""
        logger.debug("Calling registered functions")
        while self.funcs:
            try:
                self.funcs[-1]()
            except Exception as exc:  # pylint: disable=broad-except
                output = traceback.format_exception_only(type(exc), exc)
                logger.error("Encountered exception during recovery: %s",
                             ''.join(output).rstrip())
            self.funcs.pop()