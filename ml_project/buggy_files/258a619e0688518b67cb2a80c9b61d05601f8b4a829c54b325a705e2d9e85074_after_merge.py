        def _get_request():
            return self.session.get_data(
                self._mkurl(cmd, *args), should_parse=daap_data)