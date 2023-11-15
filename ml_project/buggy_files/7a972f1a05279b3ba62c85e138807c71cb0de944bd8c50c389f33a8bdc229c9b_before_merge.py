    def recent_events(self, events):
        for e in self.exports:
            recent = [d for d in e.fetch()]
            if recent:
                e.status, e.progress = recent[-1]
            if e.canceled:
                e.status = 'Export has been canceled.'