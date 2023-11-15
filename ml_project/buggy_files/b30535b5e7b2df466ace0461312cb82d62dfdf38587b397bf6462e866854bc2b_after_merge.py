    def _get_page(self, task, config, url):
        self._login(task, config)

        try:
            page_response = requests.get(url)
            if page_response.url != url:
                raise plugin.PluginError('Unexpected page: {} (expected {})'.format(page_response.url, url))

            return page_response
        except RequestException as e:
            raise plugin.PluginError('Request error: %s' % e.args[0])