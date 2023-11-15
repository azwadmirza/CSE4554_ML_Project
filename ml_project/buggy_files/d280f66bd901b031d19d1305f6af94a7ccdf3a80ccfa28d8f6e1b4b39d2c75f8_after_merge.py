    def stop_timer(self, start):

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
                    "type": "timer"
                },
                '$inc': {"count": 1, "totalTime": self._time_in_millis() - start}
            },
            upsert=True
        )