    def save(self):
        '''Apply all configuration values to the underlying storage.'''
        s = self._read_from_storage()  # type: _Settings

        for k, v in self.__dict__.items():
            if k[0] == '_':
                continue
            if hasattr(s, k):
                setattr(s, k, v)

        log.debug("_ConfigSQL updating storage")
        self._session.merge(s)
        self._session.commit()
        self.load()