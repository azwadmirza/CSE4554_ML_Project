    def get(self, cmd, daap_data=True, **args):
        """Perform a DAAP GET command."""
        def _get_request(url):
            return self.session.get_data(url, should_parse=daap_data)

        yield from self._assure_logged_in()
        return (yield from self._do(_get_request,
                                    self._mkurl(cmd, *args),
                                    is_daap=daap_data))