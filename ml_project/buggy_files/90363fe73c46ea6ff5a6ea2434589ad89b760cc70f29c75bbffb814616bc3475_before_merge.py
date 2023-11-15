    def start(self):
        self._shutdown = False

        eventlet.spawn(self.run)
        eventlet.spawn(self.cleanup)