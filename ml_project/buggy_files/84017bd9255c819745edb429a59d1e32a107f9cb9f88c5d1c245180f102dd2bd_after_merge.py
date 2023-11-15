    def restart(self, interval=None, repeats=None, start_delay=None):
        """
        Restarts an already existing/running Script from the
        beginning, optionally using different settings. This will
        first call the stop hooks, and then the start hooks again.
        Args:
            interval (int, optional): Allows for changing the interval
                of the Script. Given in seconds.  if `None`, will use the already stored interval.
            repeats (int, optional): The number of repeats. If unset, will
                use the previous setting.
            start_delay (bool, optional): If we should wait `interval` seconds
                before starting or not. If `None`, re-use the previous setting.

        """
        try:
            self.at_stop()
        except Exception:
            logger.log_trace()
        self._stop_task()
        self.is_active = False
        # remove all pause flags
        del self.db._paused_time
        del self.db._manual_pause
        del self.db._paused_callcount
        # set new flags and start over
        if interval is not None:
            if interval < 0:
                interval = 0
            self.interval = interval
        if repeats is not None:
            self.repeats = repeats
        if start_delay is not None:
            self.start_delay = start_delay
        self.start()