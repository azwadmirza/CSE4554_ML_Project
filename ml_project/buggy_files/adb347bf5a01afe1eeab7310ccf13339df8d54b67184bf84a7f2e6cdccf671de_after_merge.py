    def get(self, name, default=None):
        try:
            return self.resolved[name]
        except KeyError:
            try:
                if name in self._lookupstack:
                    raise KeyError(name)
                val = self.definitions[name]
            except KeyError:
                return os.environ.get(name, default)
            self._lookupstack.append(name)
            try:
                self.resolved[name] = res = self.reader._replace(val, name="setenv")
            finally:
                self._lookupstack.pop()
            return res