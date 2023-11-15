    def min_roi_reached(self, trade: Trade, current_profit: float, current_time: datetime) -> bool:
        """
        Based an earlier trade and current price and ROI configuration, decides whether bot should
        sell. Requires current_profit to be in percent!!
        :return True if bot should sell at current rate
        """

        # Check if time matches and current rate is above threshold
        trade_dur = (current_time.timestamp() - trade.open_date.timestamp()) / 60

        # Get highest entry in ROI dict where key <= trade-duration
        roi_list = list(filter(lambda x: x <= trade_dur, self.minimal_roi.keys()))
        if not roi_list:
            return False
        roi_entry = max(roi_list)
        threshold = self.minimal_roi[roi_entry]
        return current_profit > threshold