    def recent_events(self, events):
        for e in self.exports:
            try:
                recent = [d for d in e.fetch()]
            except Exception as e:
                self.status, self.progress = '{}: {}'.format(type(e).__name__, e), 0
            else:
                if recent:
                    e.status, e.progress = recent[-1]
                if e.canceled:
                    e.status = 'Export has been canceled.'