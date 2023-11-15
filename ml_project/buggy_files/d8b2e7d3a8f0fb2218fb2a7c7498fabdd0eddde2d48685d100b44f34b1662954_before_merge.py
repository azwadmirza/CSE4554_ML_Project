    def start_webhook(self,
                      listen='127.0.0.1',
                      port=80,
                      url_path='',
                      cert=None,
                      key=None,
                      clean=False,
                      bootstrap_retries=0,
                      webhook_url=None):
        """
        Starts a small http server to listen for updates via webhook. If cert
        and key are not provided, the webhook will be started directly on
        http://listen:port/url_path, so SSL can be handled by another
        application. Else, the webhook will be started on
        https://listen:port/url_path

        Args:
            listen (Optional[str]): IP-Address to listen on
            port (Optional[int]): Port the bot should be listening on
            url_path (Optional[str]): Path inside url
            cert (Optional[str]): Path to the SSL certificate file
            key (Optional[str]): Path to the SSL key file
            clean (Optional[bool]): Whether to clean any pending updates on
                Telegram servers before actually starting the webhook. Default
                is False.
            bootstrap_retries (Optional[int[): Whether the bootstrapping phase
                of the `Updater` will retry on failures on the Telegram server.

                |   < 0 - retry indefinitely
                |   0 - no retries (default)
                |   > 0 - retry up to X times
            webhook_url (Optional[str]): Explicitly specifiy the webhook url.
                Useful behind NAT, reverse proxy, etc. Default is derived from
                `listen`, `port` & `url_path`.

        Returns:
            Queue: The update queue that can be filled from the main thread

        """
        with self.__lock:
            if not self.running:
                self.running = True
                if clean:
                    self._clean_updates()

                # Create & start threads
                self._init_thread(self.dispatcher.start, "dispatcher"),
                self._init_thread(self._start_webhook, "updater", listen,
                                  port, url_path, cert, key, bootstrap_retries,
                                  webhook_url)

                # Return the update queue so the main thread can insert updates
                return self.update_queue