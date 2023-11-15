    def check_handler(self) -> None:
        """ Check handler executed after the poll backend returns.

        Note:
        - For each of the watchers in the ready state there will be a callback,
          which will do work related to the watcher (e.g. read from a socket).
          This time must not be accounted for in the Idle timeout, therefore
          this handler must have a high priority.
        """
        curr_time = time.time()

        # It is possible for the check_handler to be executed before the
        # prepare_handler, this happens when the watchers are installed by a
        # greenlet that was switched onto because of IO (IOW, Idle.enable is
        # called while the event loop is executing watchers, after the `poll`)
        if self.before_poll is not None:
            self.measurements.append(  # pylint: disable=no-member
                IdleMeasurement(self.before_poll, curr_time)
            )

            while curr_time - self.measurements_start > self.measurement_interval:
                self.measurements.pop()  # pylint: disable=no-member

        if curr_time - self.last_print >= self.measurement_interval:
            self.log()
            self.last_print = curr_time