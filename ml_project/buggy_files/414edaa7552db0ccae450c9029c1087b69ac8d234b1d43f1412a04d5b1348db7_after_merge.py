    def deactivate(self):
        self.active = False
        for t in self.threads:
            t.join()
        self.threads = []
        self.clear()