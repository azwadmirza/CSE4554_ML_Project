        def _get_request(url):
            return self.session.get_data(url, should_parse=daap_data)