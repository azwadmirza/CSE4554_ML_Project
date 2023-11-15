    def abort_grading(self) -> None:
        """
        Forcefully terminates the current submission. Not necessarily safe.
        """
        # Grab a local copy since it might get set to None after we do our None check.
        worker = self.current_judge_worker
        if worker:
            worker.abort_grading()