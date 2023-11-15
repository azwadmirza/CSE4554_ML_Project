    def convert(self, path, value):
        for rexp in self.map.keys():
            if rexp.match(path):
                return self.map[rexp](value)
        return value