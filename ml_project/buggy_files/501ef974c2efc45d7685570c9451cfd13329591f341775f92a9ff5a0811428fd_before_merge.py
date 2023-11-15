    def _start_webhook(self, listen, port, url_path, cert, key,
                       bootstrap_retries, webhook_url):
        self.logger.debug('Updater thread started')
        use_ssl = cert is not None and key is not None
        if not url_path.startswith('/'):
            url_path = '/{0}'.format(url_path)

        # Create and start server
        self.httpd = WebhookServer((listen, port), WebhookHandler,
                                   self.update_queue, url_path)

        if use_ssl:
            self._check_ssl_cert(cert, key)

            # DO NOT CHANGE: Only set webhook if SSL is handled by library
            if not webhook_url:
                webhook_url = self._gen_webhook_url(listen, port, url_path)

            self._set_webhook(webhook_url, bootstrap_retries,
                              open(cert, 'rb'))

        self.httpd.serve_forever(poll_interval=1)