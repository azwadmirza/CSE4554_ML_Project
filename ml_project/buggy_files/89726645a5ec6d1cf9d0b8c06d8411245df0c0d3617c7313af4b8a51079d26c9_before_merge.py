    def _setdefaultopt(self, d, alt, value):
        for opt in alt[1:]:
            try:
                return d[opt]
            except KeyError:
                pass
        value = os.path.normpath(value)
        dir_path = os.path.dirname(value)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return d.setdefault(alt[0], value)