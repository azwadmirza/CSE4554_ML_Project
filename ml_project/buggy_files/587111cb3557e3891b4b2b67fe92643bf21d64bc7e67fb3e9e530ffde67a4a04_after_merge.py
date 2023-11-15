    def configure_proxy(self, project):
        """HTTPS Proxy."""
        self.install_mobsf_ca('install')
        proxy_port = settings.PROXY_PORT
        logger.info('Starting HTTPs Proxy on %s', proxy_port)
        stop_httptools(proxy_port)
        start_proxy(proxy_port, project)