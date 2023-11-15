    def login(self):
        """Login to Apple TV using specified login id."""
        # Do not use session.get_data(...) in login as that would end up in
        # an infinte loop.
        url = self._mkurl('login?[AUTH]&hasFP=1', session=False, login_id=True)
        resp = yield from self._do(self.session.get_data, url)
        self._session_id = dmap.first(resp, 'mlog', 'mlid')
        _LOGGER.info('Logged in and got session id %s', self._session_id)
        return self._session_id