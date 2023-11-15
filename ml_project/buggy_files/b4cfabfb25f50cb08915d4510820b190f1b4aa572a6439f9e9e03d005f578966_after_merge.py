    def on_order_cancelled(self, response):
        if not response:
            return
        self.load_orders()