    def adjust_min_max_rates(self, current_price: float):
        """
        Adjust the max_rate and min_rate.
        """
        self.max_rate = max(current_price, self.max_rate or self.open_rate)
        self.min_rate = min(current_price, self.min_rate or self.open_rate)