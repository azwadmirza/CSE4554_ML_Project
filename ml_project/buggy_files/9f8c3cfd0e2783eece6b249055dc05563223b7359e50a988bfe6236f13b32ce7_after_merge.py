    def _start_polling(self, poll_interval, timeout, read_latency, bootstrap_retries, clean,
                       allowed_updates, ready=None):  # pragma: no cover
        # Thread target of thread 'updater'. Runs in background, pulls
        # updates from Telegram and inserts them in the update queue of the
        # Dispatcher.

        self.logger.debug('Updater thread started (polling)')

        self._bootstrap(bootstrap_retries, clean=clean, webhook_url='', allowed_updates=None)

        self.logger.debug('Bootstrap done')

        def polling_action_cb():
            updates = self.bot.get_updates(self.last_update_id,
                                           timeout=timeout,
                                           read_latency=read_latency,
                                           allowed_updates=allowed_updates)

            if updates:
                if not self.running:
                    self.logger.debug('Updates ignored and will be pulled again on restart')
                else:
                    for update in updates:
                        self.update_queue.put(update)
                    self.last_update_id = updates[-1].update_id + 1

            return True

        def polling_onerr_cb(exc):
            # Put the error into the update queue and let the Dispatcher
            # broadcast it
            self.update_queue.put(exc)

        if ready is not None:
            ready.set()

        self._network_loop_retry(polling_action_cb, polling_onerr_cb, 'getting Updates',
                                 poll_interval)