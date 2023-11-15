    def next_run(self):
        """Return when backlog should run next."""
        if self.action._last_backlog <= 1:
            return datetime.date.today()
        else:
            backlog_frequency_in_days = int(self.action.cycleTime)
            return datetime.date.fromordinal(self.action._last_backlog + backlog_frequency_in_days)