        def on_done(future):
            if not self._stopped:
                self._loop.add_future(invoke(), on_done)
            ex = future.exception()
            if ex is not None:
                log.error("Error thrown from periodic callback:")
                if six.PY2:
                    lines = format_exception(*future.exc_info())
                else:
                    lines = format_exception(ex.__class__, ex, ex.__traceback__)
                log.error("".join(lines))