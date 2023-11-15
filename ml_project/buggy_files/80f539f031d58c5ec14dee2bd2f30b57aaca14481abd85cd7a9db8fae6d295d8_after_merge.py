    def _get_time(self):
        time.tzset()
        if six.PY3:
            now = datetime.now(timezone.utc).astimezone()
        else:
            now = datetime.now()
        return (now + self.DELTA).strftime(self.format)