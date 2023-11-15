    def on_received_asks(self, asks):
        if not asks:
            return
        self.asks = asks["asks"]
        self.update_filter_asks_list()
        self.update_filter_bids_list()