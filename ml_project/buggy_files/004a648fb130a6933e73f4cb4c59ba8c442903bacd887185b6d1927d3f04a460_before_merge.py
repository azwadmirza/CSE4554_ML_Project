    def on_received_asks(self, asks):
        self.asks = asks["asks"]
        self.update_filter_asks_list()
        self.update_filter_bids_list()