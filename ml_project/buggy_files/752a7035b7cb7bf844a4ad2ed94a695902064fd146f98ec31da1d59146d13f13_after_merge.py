    def _getdict(self, value, default, sep, replace=True):
        if value is None or not replace:
            return default or {}

        d = {}
        for line in value.split(sep):
            if line.strip():
                name, rest = line.split('=', 1)
                d[name.strip()] = rest.strip()

        return d