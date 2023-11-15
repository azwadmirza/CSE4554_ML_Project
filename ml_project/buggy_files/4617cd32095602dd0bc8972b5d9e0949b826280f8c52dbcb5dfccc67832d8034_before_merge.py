    def next_run(self):
        """Return when backlog should run next."""
        if self.action._last_backlog <= 1:
            return datetime.date.today()
        else:
            return datetime.date.fromordinal(self.action._last_backlog + self.action.cycleTime)