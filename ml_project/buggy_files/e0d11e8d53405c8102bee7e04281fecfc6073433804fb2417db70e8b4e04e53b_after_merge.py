    def abort_grading(self) -> None:
        """
        Forcefully terminates the current submission. Not necessarily safe.
        """
        with self._current_submission_lock:
            if self.current_judge_worker:
                logger.info('Received abortion request for %d', self.current_submission.id)
                self.current_judge_worker.abort_grading()
            else:
                # This can happen because message delivery is async; the user may have pressed "Abort" before we
                # finished grading, but by the time the message reached us we may have finished grading already.
                logger.info('Received abortion request, but nothing is running')