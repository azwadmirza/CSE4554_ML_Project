    def start_polling(self,
                      poll_interval=0.0,
                      timeout=10,
                      clean=False,
                      bootstrap_retries=-1,
                      read_latency=2.,
                      allowed_updates=None):
        """Starts polling updates from Telegram.

        Args:
            poll_interval (:obj:`float`, optional): Time to wait between polling updates from
                Telegram in seconds. Default is 0.0.
            timeout (:obj:`float`, optional): Passed to :attr:`telegram.Bot.get_updates`.
            clean (:obj:`bool`, optional): Whether to clean any pending updates on Telegram servers
                before actually starting to poll. Default is :obj:`False`.
            bootstrap_retries (:obj:`int`, optional): Whether the bootstrapping phase of the
                `Updater` will retry on failures on the Telegram server.

                * < 0 - retry indefinitely (default)
                *   0 - no retries
                * > 0 - retry up to X times

            allowed_updates (List[:obj:`str`], optional): Passed to
                :attr:`telegram.Bot.get_updates`.
            read_latency (:obj:`float` | :obj:`int`, optional): Grace time in seconds for receiving
                the reply from server. Will be added to the `timeout` value and used as the read
                timeout from server (Default: 2).

        Returns:
            :obj:`Queue`: The update queue that can be filled from the main thread.

        """
        with self.__lock:
            if not self.running:
                self.running = True

                # Create & start threads
                self.job_queue.start()
                dispatcher_ready = Event()
                polling_ready = Event()
                self._init_thread(self.dispatcher.start, "dispatcher", ready=dispatcher_ready)
                self._init_thread(self._start_polling, "updater", poll_interval, timeout,
                                  read_latency, bootstrap_retries, clean, allowed_updates,
                                  ready=polling_ready)

                self.logger.debug('Waiting for Dispatcher and polling to start')
                dispatcher_ready.wait()
                polling_ready.wait()

                # Return the update queue so the main thread can insert updates
                return self.update_queue