        def on_done(future):
            if not self._stopped:
                self._loop.add_future(invoke(), on_done)
            if future.exception() is not None:
                log.error("Error thrown from periodic callback:")
                log.error("".join(format_exception(*future.exc_info())))