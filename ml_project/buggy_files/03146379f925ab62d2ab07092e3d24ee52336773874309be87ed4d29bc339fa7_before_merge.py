    def acknowledge(self):
        if not self._has_message:
            raise exceptions.PipelineError("No message to acknowledge.")
        self._acknowledge()
        self._has_message = False