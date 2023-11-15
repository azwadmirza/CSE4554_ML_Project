    def session(self):
        """
        Returns a valid botocore session
        """
        if self._session is None:
            self._session = get_session()
        return self._session