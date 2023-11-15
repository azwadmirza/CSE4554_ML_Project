    def read(self):
        for msg in self.queue:
            yield msg+'\n'
        queue = []