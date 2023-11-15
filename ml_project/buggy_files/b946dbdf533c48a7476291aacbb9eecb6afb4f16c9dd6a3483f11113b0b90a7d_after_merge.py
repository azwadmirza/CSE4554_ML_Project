    def __contains__(self, path):
        if super().__contains__(path):
            return True
        return path in self.passthroughdict