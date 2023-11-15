    def connection_lost(self, exc):
        """Lose connection to host."""
        self.semaphore.release()