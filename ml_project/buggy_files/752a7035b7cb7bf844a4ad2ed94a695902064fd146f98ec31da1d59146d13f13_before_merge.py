    def _getdict(self, value, default, sep):
        if value is None:
            return default or {}

        d = {}
        for line in value.split(sep):
            if line.strip():
                name, rest = line.split('=', 1)
                d[name.strip()] = rest.strip()

        return d