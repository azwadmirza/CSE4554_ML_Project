    def start(self):
        if not self.uris:
            return
        self.next_uri()
        self.loop.run()