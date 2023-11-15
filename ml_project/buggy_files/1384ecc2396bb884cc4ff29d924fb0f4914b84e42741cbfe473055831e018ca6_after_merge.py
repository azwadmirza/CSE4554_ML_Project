    def _do_request(self, method, path, query_string=None, headers=None, body=None):
        '''Send request, read and return response object'''

        log.debug('started with %s %s, qs=%s', method, path, query_string)

        if headers is None:
            headers = CaseInsensitiveDict()

        expect100 = isinstance(body, BodyFollowing)
        headers['host'] = self.hostname
        if query_string:
            s = urllib.parse.urlencode(query_string, doseq=True)
            path += '?%s' % s

        # If we have an access token, try to use it.
        token = self.access_token.get(self.refresh_token, None)
        if token is not None:
            headers['Authorization'] = 'Bearer ' + token
            self.conn.send_request(method, path, body=body, headers=headers,
                                   expect100=expect100)
            resp = self.conn.read_response()
            if ((expect100 and resp.status == 100) or
                (not expect100 and 200 <= resp.status <= 299)):
                return resp
            elif resp.status != 401:
                raise self._parse_error_response(resp)
            self.conn.discard()

        # If we reach this point, then the access token must have
        # expired, so we try to get a new one. We use a lock to prevent
        # multiple threads from refreshing the token simultaneously.
        with self._refresh_lock:
            # Don't refresh if another thread has already done so while
            # we waited for the lock.
            if token is None or self.access_token.get(self.refresh_token, None) == token:
                self._get_access_token()

        # Try request again. If this still fails, propagate the error
        # (because we have just refreshed the access token).
        # FIXME: We can't rely on this if e.g. the system hibernated
        # after refreshing the token, but before reaching this line.
        headers['Authorization'] = 'Bearer ' + self.access_token[self.refresh_token]
        self.conn.send_request(method, path, body=body, headers=headers,
                               expect100=expect100)
        resp = self.conn.read_response()
        if ((expect100 and resp.status == 100) or
            (not expect100 and 200 <= resp.status <= 299)):
            return resp
        else:
            raise self._parse_error_response(resp)