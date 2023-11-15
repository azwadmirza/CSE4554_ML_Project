    def _grading_thread_main(self, ipc_ready_signal: threading.Event, submission: Submission, report) -> None:
        try:
            report(
                ansi_style(
                    'Start grading #ansi[%s](yellow)/#ansi[%s](green|bold) in %s...'
                    % (submission.problem_id, submission.id, submission.language)
                )
            )

            self.current_judge_worker = JudgeWorker(submission)

            ipc_handler_dispatch: Dict[IPC, Callable] = {
                IPC.HELLO: lambda _report: ipc_ready_signal.set(),
                IPC.COMPILE_ERROR: self._ipc_compile_error,
                IPC.COMPILE_MESSAGE: self._ipc_compile_message,
                IPC.GRADING_BEGIN: self._ipc_grading_begin,
                IPC.GRADING_END: self._ipc_grading_end,
                IPC.GRADING_ABORTED: self._ipc_grading_aborted,
                IPC.BATCH_BEGIN: self._ipc_batch_begin,
                IPC.BATCH_END: self._ipc_batch_end,
                IPC.RESULT: self._ipc_result,
                IPC.UNHANDLED_EXCEPTION: self._ipc_unhandled_exception,
            }

            for ipc_type, data in self.current_judge_worker.communicate():
                try:
                    handler_func = ipc_handler_dispatch[ipc_type]
                except KeyError:
                    raise RuntimeError(
                        "judge got unexpected IPC message from worker: %s" % ((ipc_type, data),)
                    ) from None

                handler_func(report, *data)

            report(
                ansi_style(
                    'Done grading #ansi[%s](yellow)/#ansi[%s](green|bold).\n' % (submission.problem_id, submission.id)
                )
            )
        except Exception:  # noqa: E722, we want to catch everything
            self.log_internal_error()
        finally:
            if self.current_judge_worker is not None:
                self.current_judge_worker.stop()

            self.current_submission = None
            self.current_judge_worker = None

            # Might not have been set if an exception was encountered before HELLO message, so signal here to keep the
            # other side from waiting forever.
            ipc_ready_signal.set()