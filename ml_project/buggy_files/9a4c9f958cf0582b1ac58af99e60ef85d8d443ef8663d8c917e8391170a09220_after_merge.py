    def read(self):
        for msg in self.queue:
            yield msg
        queue = []