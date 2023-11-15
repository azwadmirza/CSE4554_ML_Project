    def shutdown(self):
        if not self.should_exit.is_set():
            self.should_exit.set()
            if self.server:
                self.server.shutdown()