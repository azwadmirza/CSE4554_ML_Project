    def _do(self, action, url, retry=True, is_login=False, is_daap=True):
        resp, status = yield from action(url)
        self._log_response(str(action.__name__) + ': %s', resp, is_daap)
        if status >= 200 and status < 300:
            return resp

        # Retry once if we got a bad response, otherwise bail out
        if retry:
            return (yield from self._do(
                action, url, False, is_login=is_login, is_daap=is_daap))
        else:
            raise exceptions.AuthenticationError(
                'failed to login: ' + str(status))