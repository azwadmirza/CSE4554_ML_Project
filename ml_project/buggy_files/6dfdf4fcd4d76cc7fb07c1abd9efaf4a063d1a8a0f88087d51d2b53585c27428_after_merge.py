    def _start_webhook(self, listen, port, url_path, cert, key, bootstrap_retries, clean,
                       webhook_url, allowed_updates, ready=None, force_event_loop=False):
        self.logger.debug('Updater thread started (webhook)')
        use_ssl = cert is not None and key is not None
        if not url_path.startswith('/'):
            url_path = '/{}'.format(url_path)

        # Create Tornado app instance
        app = WebhookAppClass(url_path, self.bot, self.update_queue,
                              default_quote=self._default_quote)

        # Form SSL Context
        # An SSLError is raised if the private key does not match with the certificate
        if use_ssl:
            try:
                ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ssl_ctx.load_cert_chain(cert, key)
            except ssl.SSLError:
                raise TelegramError('Invalid SSL Certificate')
        else:
            ssl_ctx = None

        # Create and start server
        self.httpd = WebhookServer(listen, port, app, ssl_ctx)

        if use_ssl:
            # DO NOT CHANGE: Only set webhook if SSL is handled by library
            if not webhook_url:
                webhook_url = self._gen_webhook_url(listen, port, url_path)

            self._bootstrap(max_retries=bootstrap_retries,
                            clean=clean,
                            webhook_url=webhook_url,
                            cert=open(cert, 'rb'),
                            allowed_updates=allowed_updates)
        elif clean:
            self.logger.warning("cleaning updates is not supported if "
                                "SSL-termination happens elsewhere; skipping")

        self.httpd.serve_forever(force_event_loop=force_event_loop, ready=ready)