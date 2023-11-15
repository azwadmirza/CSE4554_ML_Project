    def convert(self, value, view):
        if isinstance(value, bytes):
            value = value.decode('utf8', 'ignore')

        if isinstance(value, STRING):
            if self.split:
                return value.split()
            else:
                return [value]
        else:
            try:
                value = list(value)
            except TypeError:
                self.fail('must be a whitespace-separated string or a list',
                          view, True)
            if all(isinstance(x, BASESTRING) for x in value):
                return value
            else:
                self.fail('must be a list of strings', view, True)