    def connect(self):
        """Return a raw database connection object."""
        return self.engine.connect()