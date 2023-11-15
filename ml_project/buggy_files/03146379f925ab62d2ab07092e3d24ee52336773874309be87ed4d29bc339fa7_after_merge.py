    def acknowledge(self):
        """
        Acknowledge/delete the current message from the source queue

        Parameters
        ----------

        Raises
        ------
        exceptions
            exceptions.PipelineError: If no message is held

        Returns
        -------
        None.

        """
        if not self._has_message:
            raise exceptions.PipelineError("No message to acknowledge.")
        self._acknowledge()
        self._has_message = False