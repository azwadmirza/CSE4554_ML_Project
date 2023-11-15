    def filter(self, record):
        return not any(f.filter(record) for f in self.blacklist)