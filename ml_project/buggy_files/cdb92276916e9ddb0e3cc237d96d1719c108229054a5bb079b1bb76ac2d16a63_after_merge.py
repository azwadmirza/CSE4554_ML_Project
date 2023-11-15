    def connect(self):
        """Return a raw database connection object."""
        return sqlite3.connect(self.filename, timeout=10)