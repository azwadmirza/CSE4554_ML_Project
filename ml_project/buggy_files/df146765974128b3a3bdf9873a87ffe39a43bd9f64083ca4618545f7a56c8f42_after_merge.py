    def _start_polling(self, poll_interval, timeout, network_delay,
                       bootstrap_retries, clean):
        """
        Thread target of thread 'updater'. Runs in background, pulls
        updates from Telegram and inserts them in the update queue of the
        Dispatcher.

        """
        cur_interval = poll_interval
        self.logger.debug('Updater thread started')

        self._bootstrap(bootstrap_retries, clean=clean, webhook_url='')

        while self.running:
            try:
                updates = self.bot.getUpdates(self.last_update_id,
                                              timeout=timeout,
                                              network_delay=network_delay)
            except TelegramError as te:
                self.logger.error(
                    "Error while getting Updates: {0}".format(te))

                # Put the error into the update queue and let the Dispatcher
                # broadcast it
                self.update_queue.put(te)

                cur_interval = self._increase_poll_interval(cur_interval)
            else:
                if not self.running:
                    if len(updates) > 0:
                        self.logger.debug('Updates ignored and will be pulled '
                                          'again on restart.')
                    break

                if updates:
                    for update in updates:
                        self.update_queue.put(update)
                    self.last_update_id = updates[-1].update_id + 1

                cur_interval = poll_interval

            sleep(cur_interval)