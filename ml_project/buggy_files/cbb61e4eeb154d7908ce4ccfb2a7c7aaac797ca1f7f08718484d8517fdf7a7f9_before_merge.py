    def _call_registered(self):
        """Calls all registered functions"""
        logger.debug("Calling registered functions")
        while self.funcs:
            try:
                self.funcs[-1]()
            except Exception:  # pylint: disable=broad-except
                logger.error("Encountered exception during recovery: ", exc_info=True)
            self.funcs.pop()