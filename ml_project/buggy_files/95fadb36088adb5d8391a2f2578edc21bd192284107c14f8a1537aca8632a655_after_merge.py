    def _worker(self, old_state: Optional[State]) -> State:
        """
        The main routine that runs each throttling iteration and handles the states.
        :param old_state: the previous service state from the previous call
        :return: current service state
        """
        state = self.freqtrade.state

        # Log state transition
        if state != old_state:
            self.freqtrade.notify_status(f'{state.name.lower()}')

            logger.info(f"Changing state to: {state.name}")
            if state == State.RUNNING:
                self.freqtrade.startup()

            # Reset heartbeat timestamp to log the heartbeat message at
            # first throttling iteration when the state changes
            self._heartbeat_msg = 0

        if state == State.STOPPED:
            # Ping systemd watchdog before sleeping in the stopped state
            if self._sd_notify:
                logger.debug("sd_notify: WATCHDOG=1\\nSTATUS=State: STOPPED.")
                self._sd_notify.notify("WATCHDOG=1\nSTATUS=State: STOPPED.")

            self._throttle(func=self._process_stopped, throttle_secs=self._throttle_secs)

        elif state == State.RUNNING:
            # Ping systemd watchdog before throttling
            if self._sd_notify:
                logger.debug("sd_notify: WATCHDOG=1\\nSTATUS=State: RUNNING.")
                self._sd_notify.notify("WATCHDOG=1\nSTATUS=State: RUNNING.")

            self._throttle(func=self._process_running, throttle_secs=self._throttle_secs)

        if self._heartbeat_interval:
            now = time.time()
            if (now - self._heartbeat_msg) > self._heartbeat_interval:
                logger.info(f"Bot heartbeat. PID={getpid()}, "
                            f"version='{__version__}', state='{state.name}'")
                self._heartbeat_msg = now

        return state