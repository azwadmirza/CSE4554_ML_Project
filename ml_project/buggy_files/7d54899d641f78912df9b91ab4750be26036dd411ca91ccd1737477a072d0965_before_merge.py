    def start(self):
        if self._started:
            raise RuntimeError("called start() twice on _AsyncPeriodic")
        self._started = True

        def invoke():
            # important to start the sleep before starting callback
            # so any initial time spent in callback "counts against"
            # the period.
            sleep_future = self.sleep()
            result = self._func()

            # This is needed for Tornado >= 4.5 where convert_yielded will no
            # longer raise BadYieldError on None
            if result is None:
                return sleep_future

            try:
                callback_future = gen.convert_yielded(result)
            except gen.BadYieldError:
                # result is not a yieldable thing
                return sleep_future
            else:
                return gen.multi([sleep_future, callback_future])

        def on_done(future):
            if not self._stopped:
                self._loop.add_future(invoke(), on_done)
            if future.exception() is not None:
                log.error("Error thrown from periodic callback:")
                log.error("".join(format_exception(*future.exc_info())))

        self._loop.add_future(self.sleep(), on_done)