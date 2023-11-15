    def _worker_process_main(
        self,
        judge_process_conn: 'multiprocessing.connection.Connection',
        worker_process_conn: 'multiprocessing.connection.Connection',
    ) -> None:
        """
        Main body of judge worker process, which handles grading and sends grading results to the judge controller via
        IPC.
        """
        worker_process_conn.close()
        setproctitle(multiprocessing.current_process().name)

        def _ipc_recv_thread_main() -> None:
            """
            Worker thread that listens for incoming IPC messages from the judge controller.
            """
            while True:
                try:
                    ipc_type, data = judge_process_conn.recv()
                except:  # noqa: E722, whatever happened, we have to abort now.
                    logger.exception("Judge unexpectedly hung up!")
                    self._do_abort()
                    return

                if ipc_type == IPC.BYE:
                    return
                elif ipc_type == IPC.REQUEST_ABORT:
                    self._do_abort()
                else:
                    raise RuntimeError("worker got unexpected IPC message from judge: %s" % ((ipc_type, data),))

        def _report_unhandled_exception() -> None:
            # We can't pickle the whole traceback object, so just send the formatted exception.
            message = ''.join(traceback.format_exception(*sys.exc_info()))
            judge_process_conn.send((IPC.UNHANDLED_EXCEPTION, (message,)))
            judge_process_conn.send((IPC.BYE, ()))

        ipc_recv_thread = None
        try:
            judge_process_conn.send((IPC.HELLO, ()))

            ipc_recv_thread = threading.Thread(target=_ipc_recv_thread_main, daemon=True)
            ipc_recv_thread.start()

            case_gen = self._grade_cases()
            while True:
                try:
                    ipc_msg = next(case_gen)
                except StopIteration:
                    break
                except BrokenPipeError:
                    # A grader can raise a `BrokenPipeError` that's indistinguishable from one caused by
                    # `judge_process_conn.send`, but should be handled differently (i.e. not quit the judge).
                    _report_unhandled_exception()
                    return

                judge_process_conn.send(ipc_msg)

            judge_process_conn.send((IPC.BYE, ()))
        except BrokenPipeError:
            # There's nothing we can do about this... the general except branch would just fail again. Just re-raise and
            # hope for the best.
            raise
        except:  # noqa: E722, we explicitly want to notify the parent of everything
            _report_unhandled_exception()
        finally:
            if ipc_recv_thread is not None:
                # We may have failed before sending the IPC.BYE down the connection, in which case the judge will never
                # close its side of the connection -- so `ipc_recv_thread` will never exit. But we can't wait forever in
                # this case, since we're blocking the main judge from proceeding.
                ipc_recv_thread.join(timeout=IPC_TEARDOWN_TIMEOUT)
                if ipc_recv_thread.is_alive():
                    logger.error("Judge IPC recv thread is still alive after timeout, shutting worker down anyway!")

            # FIXME(tbrindus): we need to do this because cleaning up temporary directories happens on __del__, which
            # won't get called if we exit the process right now (so we'd leak all files created by the grader). This
            # should be refactored to have an explicit `cleanup()` or similar, rather than relying on refcounting
            # working out.
            self.grader = None