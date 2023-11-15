        def _on_failure(failure):
            self._logger.error("Error when processing channel dir download: %s", failure)
            self.processing = False