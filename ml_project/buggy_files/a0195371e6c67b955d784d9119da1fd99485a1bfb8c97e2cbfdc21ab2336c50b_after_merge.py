    def on_received_bids(self, bids):
        if not bids:
            return
        self.bids = bids["bids"]
        self.update_filter_asks_list()
        self.update_filter_bids_list()