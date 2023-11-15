    def cleanup(self):
        """Delete expired meta-data."""
        self.collection.delete_many(
            {'date_done': {'$lt': self.app.now() - self.expires_delta}},
        )
        self.group_collection.delete_many(
            {'date_done': {'$lt': self.app.now() - self.expires_delta}},
        )