    def teardown_handles(self):
        for group in self.handles['artist'].values():
            for v in group:
                v.remove()
        for group in self.handles['box'].values():
            for v in group:
                v.remove()