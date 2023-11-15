    def __getstate__(self):
        return self.to_wkt()