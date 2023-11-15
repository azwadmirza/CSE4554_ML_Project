    def start_webhook(self,
                      listen='127.0.0.1',
                      port=80,
                      url_path='',
                      cert=None,
                      key=None,
                      clean=False,
                      bootstrap_retries=0,
                      webhook_url=None,
                      allowed_updates=None,
                      force_event_loop=False):
        """
        Starts a small http server to listen for updates via webhook. If cert
        and key are not provided, the webhook will be started directly on
        http://listen:port/url_path, so SSL can be handled by another
        application. Else, the webhook will be started on
        https://listen:port/url_path

        Note:
            Due to an incompatibility of the Tornado library PTB uses for the webhook with Python
            3.8+ on Windows machines, PTB will attempt to set the event loop to
            :attr:`asyncio.SelectorEventLoop` and raise an exception, if an incompatible event loop
            has already been specified. See this `thread`_ for more details. To suppress the
            exception, set :attr:`force_event_loop` to :obj:`True`.

            .. _thread: https://github.com/tornadoweb/tornado/issues/2608

        Args:
            listen (:obj:`str`, optional): IP-Address to listen on. Default ``127.0.0.1``.
            port (:obj:`int`, optional): Port the bot should be listening on. Default ``80``.
            url_path (:obj:`str`, optional): Path inside url.
            cert (:obj:`str`, optional): Path to the SSL certificate file.
            key (:obj:`str`, optional): Path to the SSL key file.
            clean (:obj:`bool`, optional): Whether to clean any pending updates on Telegram servers
                before actually starting the webhook. Default is :obj:`False`.
            bootstrap_retries (:obj:`int`, optional): Whether the bootstrapping phase of the
                `Updater` will retry on failures on the Telegram server.

                * < 0 - retry indefinitely (default)
                *   0 - no retries
                * > 0 - retry up to X times

            webhook_url (:obj:`str`, optional): Explicitly specify the webhook url. Useful behind
                NAT, reverse proxy, etc. Default is derived from `listen`, `port` & `url_path`.
            allowed_updates (List[:obj:`str`], optional): Passed to
                :attr:`telegram.Bot.set_webhook`.
            force_event_loop (:obj:`bool`, optional): Force using the current event loop. See above
                note for details. Defaults to :obj:`False`

        Returns:
            :obj:`Queue`: The update queue that can be filled from the main thread.

        """
        with self.__lock:
            if not self.running:
                self.running = True

                # Create & start threads
                webhook_ready = Event()
                dispatcher_ready = Event()
                self.job_queue.start()
                self._init_thread(self.dispatcher.start, "dispatcher", dispatcher_ready)
                self._init_thread(self._start_webhook, "updater", listen, port, url_path, cert,
                                  key, bootstrap_retries, clean, webhook_url, allowed_updates,
                                  ready=webhook_ready, force_event_loop=force_event_loop)

                self.logger.debug('Waiting for Dispatcher and Webhook to start')
                webhook_ready.wait()
                dispatcher_ready.wait()

                # Return the update queue so the main thread can insert updates
                return self.update_queue