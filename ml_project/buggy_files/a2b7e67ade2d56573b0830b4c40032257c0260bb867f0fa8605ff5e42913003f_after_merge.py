    def get(self, cmd, daap_data=True, **args):
        """Perform a DAAP GET command."""
        def _get_request():
            return self.session.get_data(
                self._mkurl(cmd, *args), should_parse=daap_data)

        yield from self._assure_logged_in()
        return (yield from self._do(_get_request, is_daap=daap_data))