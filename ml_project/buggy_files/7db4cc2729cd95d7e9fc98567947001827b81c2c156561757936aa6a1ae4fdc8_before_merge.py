    def _apply_index_days(self, i, roll):
        i += (roll % 2) * Timedelta(days=self.day_of_month).value
        return i + Timedelta(days=-1)