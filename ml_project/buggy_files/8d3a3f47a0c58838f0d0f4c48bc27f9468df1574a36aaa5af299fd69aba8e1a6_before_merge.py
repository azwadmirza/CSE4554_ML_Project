    def inner(self, *args, **kwargs):
        if 'HttpHeaders' in self._auth_configs:
            if 'headers' not in kwargs:
                kwargs['headers'] = self._auth_configs['HttpHeaders']
            else:
                kwargs['headers'].update(self._auth_configs['HttpHeaders'])
        return f(self, *args, **kwargs)