    def on_received_orders(self, orders):
        for order in orders["orders"]:
            if self.wallets:
                asset1_prec = self.wallets[order["assets"]["first"]["type"]]["precision"]
                asset2_prec = self.wallets[order["assets"]["second"]["type"]]["precision"]
                item = OrderWidgetItem(self.window().market_orders_list, order, asset1_prec, asset2_prec)
                self.window().market_orders_list.addTopLevelItem(item)