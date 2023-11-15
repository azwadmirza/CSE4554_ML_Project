    def post(self, cmd, data=None, **args):
        """Perform DAAP POST command with optional data."""
        def _post_request(url):
            return self.session.post_data(url, data=data)

        yield from self._assure_logged_in()
        return (yield from self._do(_post_request, self._mkurl(cmd, *args)))