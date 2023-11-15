    def configure_proxy(self, project, request):
        """HTTPS Proxy."""
        self.install_mobsf_ca('install')
        proxy_port = settings.PROXY_PORT
        logger.info('Starting HTTPs Proxy on %s', proxy_port)
        httptools_url = get_http_tools_url(request)
        stop_httptools(httptools_url)
        start_proxy(proxy_port, project)