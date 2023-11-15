    def match(self, item):
        if self.field not in item:
            return False
        timestamp = float(item[self.field])
        date = datetime.utcfromtimestamp(timestamp)
        return self.interval.contains(date)