    def start_polling(self,
                      poll_interval=0.0,
                      timeout=10,
                      network_delay=2,
                      clean=False,
                      bootstrap_retries=0):
        """
        Starts polling updates from Telegram.

        Args:
            poll_interval (Optional[float]): Time to wait between polling
                updates from Telegram in seconds. Default is 0.0
            timeout (Optional[float]): Passed to Bot.getUpdates
            network_delay (Optional[float]): Passed to Bot.getUpdates
            clean (Optional[bool]): Whether to clean any pending updates on
                Telegram servers before actually starting to poll. Default is
                False.
            bootstrap_retries (Optional[int[): Whether the bootstrapping phase
                of the `Updater` will retry on failures on the Telegram server.

                |   < 0 - retry indefinitely
                |   0 - no retries (default)
                |   > 0 - retry up to X times

        Returns:
            Queue: The update queue that can be filled from the main thread

        """
        with self.__lock:
            if not self.running:
                self.running = True

                # Create & start threads
                self._init_thread(self.dispatcher.start, "dispatcher")
                self._init_thread(self._start_polling, "updater", poll_interval, timeout,
                                  network_delay, bootstrap_retries, clean)

                # Return the update queue so the main thread can insert updates
                return self.update_queue