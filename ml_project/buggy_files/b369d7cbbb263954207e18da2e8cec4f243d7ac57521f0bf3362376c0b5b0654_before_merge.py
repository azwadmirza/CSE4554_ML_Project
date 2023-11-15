    def inc(self):

        db.metrics.update_one(
            {
                "group": self.group,
                "name": self.name
            },
            {
                '$set': {
                    "group": self.group,
                    "name": self.name,
                    "title": self.title,
                    "description": self.description,
                    "type": "counter"
                },
                '$inc': {"count": 1}
            },
            True
        )