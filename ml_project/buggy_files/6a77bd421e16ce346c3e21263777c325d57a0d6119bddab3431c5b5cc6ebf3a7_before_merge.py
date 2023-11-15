    def end(self, tee_output=True):
        """Waits for the command to complete and then runs any closing and
        cleanup procedures that need to be run.
        """
        if self.ended:
            return
        if tee_output:
            for _ in self.tee_stdout():
                pass
        self._endtime()
        # since we are driven by getting output, input may not be available
        # until the command has completed.
        self._set_input()
        self._close_prev_procs()
        self._close_proc()
        self._check_signal()
        self._apply_to_history()
        self.ended = True
        self._raise_subproc_error()