    def on_order_created(self, response, is_ask):
        if is_ask:
            self.load_asks()
        else:
            self.load_bids()