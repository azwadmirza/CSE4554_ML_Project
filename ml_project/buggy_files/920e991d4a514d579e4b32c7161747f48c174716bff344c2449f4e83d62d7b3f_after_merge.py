    def _wrapper(self, pipe, _should_terminate_flag, generator, *args, **kwargs):
        """Executed in background, pipes generator results to foreground

        All exceptions are caught, forwarded to the foreground, and raised in
        `Task_Proxy.fetch()`. This allows users to handle failure gracefully
        as well as raising their own exceptions in the background task.
        """

        def interrupt_handler(sig, frame):
            import traceback

            trace = traceback.format_stack(f=frame)
            logger.debug(f"Caught signal {sig} in:\n" + "".join(trace))
            # NOTE: Interrupt is handled in world/service/player which are responsible
            # for shutting down the background process properly

        signal.signal(signal.SIGINT, interrupt_handler)
        try:
            self._change_logging_behavior()
            logger.debug("Entering _wrapper")

            for datum in generator(*args, **kwargs):
                if _should_terminate_flag.value:
                    raise EarlyCancellationError("Task was cancelled")
                pipe.send(datum)
            pipe.send(StopIteration())
        except BrokenPipeError:
            # process canceled from outside
            pass
        except Exception as e:
            try:
                pipe.send(e)
            except BrokenPipeError:
                # process canceled from outside
                pass
            if not isinstance(e, EarlyCancellationError):
                import traceback

                logger.info(traceback.format_exc())
        finally:
            pipe.close()
            logger.debug("Exiting _wrapper")