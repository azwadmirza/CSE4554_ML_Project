    def _do(self, action, retry=True, is_login=False, is_daap=True):
        resp, status = yield from action()
        self._log_response(str(action.__name__) + ': %s', resp, is_daap)
        if status >= 200 and status < 300:
            return resp

        # When a 403 is received we are likely logged out, so a new
        # login must be performed to get a new session id
        if status == 403:
            _LOGGER.info('implicitly logged out, logging in again')
            yield from self.login()

        # Retry once if we got a bad response, otherwise bail out
        if retry:
            return (yield from self._do(
                action, False, is_login=is_login, is_daap=is_daap))
        else:
            raise exceptions.AuthenticationError(
                'failed to login: ' + str(status))