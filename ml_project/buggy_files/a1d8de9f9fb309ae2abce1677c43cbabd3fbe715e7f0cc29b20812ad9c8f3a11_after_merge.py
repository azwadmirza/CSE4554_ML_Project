    def __getattribute__(self, attr):
        value = object.__getattribute__(self, attr)
        if attr.endswith('ENDPOINT'):
            verb, path = value
            url = u'{0}{1}'.format(self.KITE_URL, path)
            return verb.lower(), url
        return value