    def __init__(self, conditional, encoding=None):
        self.raw = conditional
        self.encoding = encoding or 'json'

        try:
            key, op, val = shlex.split(conditional)
        except ValueError:
            raise ValueError('failed to parse conditional')

        self.key = key
        self.func = self._func(op)
        self.value = self._cast_value(val)