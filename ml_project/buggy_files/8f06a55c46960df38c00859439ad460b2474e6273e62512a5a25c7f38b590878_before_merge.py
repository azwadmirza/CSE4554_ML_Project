    def adjust_levels(self, low: float, high: float) -> Tuple[float, float]:
        """
        Adjust the data low, high levels by applying the thresholding and
        centering.
        """
        assert low <= high
        threshold_low, threshold_high = self.thresholds
        lt = low + (high - low) * threshold_low
        ht = low + (high - low) * threshold_high
        if self.center is not None:
            center = self.center
            maxoff = max(abs(center - lt), abs(center - ht))
            lt = center - maxoff
            ht = center + maxoff
        return lt, ht