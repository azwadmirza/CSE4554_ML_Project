    def _gen_webhook_url(listen, port, url_path):
        return 'https://{listen}:{port}{path}'.format(
            listen=listen,
            port=port,
            path=url_path)