    def match(self, item):
        timestamp = float(item[self.field])
        date = datetime.utcfromtimestamp(timestamp)
        return self.interval.contains(date)