    def begin_grading(self, submission: Submission, report=logger.info, blocking=False) -> None:
        assert self.current_submission is None

        self.current_submission = submission
        ipc_ready_signal = threading.Event()
        grading_thread = threading.Thread(
            target=self._grading_thread_main, args=(ipc_ready_signal, submission, report), daemon=True
        )
        grading_thread.start()

        ipc_ready_signal.wait()
        if blocking:
            grading_thread.join()