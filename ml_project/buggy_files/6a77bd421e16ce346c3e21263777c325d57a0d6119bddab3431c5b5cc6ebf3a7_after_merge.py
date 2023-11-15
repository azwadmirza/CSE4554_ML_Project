    def end(self, tee_output=True):
        """
        End the pipeline, return the controlling terminal if needed.

        Main things done in self._end().
        """
        if self.ended:
            return
        self._end(tee_output=tee_output)
        self._return_terminal()