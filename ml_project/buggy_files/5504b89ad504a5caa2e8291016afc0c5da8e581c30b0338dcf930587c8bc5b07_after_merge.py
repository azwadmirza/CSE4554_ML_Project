    def begin_grading(self, submission: Submission, report=logger.info, blocking=False) -> None:
        # Ensure only one submission is running at a time; this lock is released at the end of submission grading.
        # This is necessary because `begin_grading` is "re-entrant"; after e.g. grading-end is sent, the network
        # thread may receive a new submission before the grading thread and worker from the *previous* submission
        # have finished tearing down. Trashing global state (e.g. `self.current_judge_worker`) before then would be
        # an error.
        self._grading_lock.acquire()
        with self._current_submission_lock:
            assert self.current_judge_worker is None

            report(
                ansi_style(
                    'Start grading #ansi[%s](yellow)/#ansi[%s](green|bold) in %s...'
                    % (submission.problem_id, submission.id, submission.language)
                )
            )

            self.current_judge_worker = JudgeWorker(submission)

            ipc_ready_signal = threading.Event()
            grading_thread = threading.Thread(
                target=self._grading_thread_main, args=(ipc_ready_signal, report), daemon=True
            )
            grading_thread.start()

        ipc_ready_signal.wait()

        if blocking:
            grading_thread.join()