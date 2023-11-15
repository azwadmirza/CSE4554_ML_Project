    def set(self, value):

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
                    "value": value,
                    "type": "gauge"
                }
            },
            upsert=True
        )