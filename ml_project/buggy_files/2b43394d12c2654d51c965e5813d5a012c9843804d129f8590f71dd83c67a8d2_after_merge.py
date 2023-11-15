    def session(self):
        """
        Returns a valid botocore session
        """
        # botocore client creation is not thread safe as of v1.2.5+ (see issue #153)
        if getattr(self._local, 'session', None) is None:
            self._local.session = get_session()
        return self._local.session