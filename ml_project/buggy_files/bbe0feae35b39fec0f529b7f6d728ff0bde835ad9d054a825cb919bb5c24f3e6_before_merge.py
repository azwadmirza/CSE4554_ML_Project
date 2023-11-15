    def _apply_index_days(self, i, roll):
        return i + (roll % 2) * Timedelta(days=self.day_of_month - 1).value