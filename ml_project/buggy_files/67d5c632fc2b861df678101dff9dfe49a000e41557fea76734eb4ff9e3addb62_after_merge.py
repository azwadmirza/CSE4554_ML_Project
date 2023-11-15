    def update_as_of(self, utc_point_in_time):
        """Calculate sun state at a point in UTC time."""
        import astral

        mod = -1
        while True:
            try:
                next_rising_dt = self.location.sunrise(
                    utc_point_in_time + timedelta(days=mod), local=False)
                if next_rising_dt > utc_point_in_time:
                    break
            except astral.AstralError:
                pass
            mod += 1

        mod = -1
        while True:
            try:
                next_setting_dt = (self.location.sunset(
                    utc_point_in_time + timedelta(days=mod), local=False))
                if next_setting_dt > utc_point_in_time:
                    break
            except astral.AstralError:
                pass
            mod += 1

        self.next_rising = next_rising_dt
        self.next_setting = next_setting_dt