    def run(self):
        """Function called to grab stats.
        Infinite loop, should be stopped by calling the stop() method"""

        for i in self._stats_stream:
            self._stats = i
            # countdown = Timer(self._refresh_time)
            # while not countdown.finished() and not is_stopped:
            #     is_stopped = self.stopped()
            #     time.sleep(0.1)
            # if is_stopped:
            #     break
            time.sleep(0.1)
            if self.stopped():
                break