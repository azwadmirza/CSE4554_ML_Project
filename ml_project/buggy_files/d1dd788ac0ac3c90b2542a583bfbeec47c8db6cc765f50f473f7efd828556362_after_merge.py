    def start(self):
        if self.next_uri():
            self.loop.run()