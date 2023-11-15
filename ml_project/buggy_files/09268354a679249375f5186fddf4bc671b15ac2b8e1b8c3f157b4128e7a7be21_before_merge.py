    def __init__(self, region=None, host=None, session_cls=None,
                 request_timeout_seconds=None, max_retry_attempts=None, base_backoff_ms=None):
        self._tables = {}
        self.host = host
        self._session = None
        self._requests_session = None
        self._client = None
        if region:
            self.region = region
        else:
            self.region = get_settings_value('region')

        if session_cls:
            self.session_cls = session_cls
        else:
            self.session_cls = get_settings_value('session_cls')

        if request_timeout_seconds is not None:
            self._request_timeout_seconds = request_timeout_seconds
        else:
            self._request_timeout_seconds = get_settings_value('request_timeout_seconds')

        if max_retry_attempts is not None:
            self._max_retry_attempts_exception = max_retry_attempts
        else:
            self._max_retry_attempts_exception = get_settings_value('max_retry_attempts')

        if base_backoff_ms is not None:
            self._base_backoff_ms = base_backoff_ms
        else:
            self._base_backoff_ms = get_settings_value('base_backoff_ms')