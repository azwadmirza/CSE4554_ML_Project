    def _get_time(self):
        time.tzset()
        now = datetime.now(utc).astimezone()
        return (now + self.DELTA).strftime(self.format)