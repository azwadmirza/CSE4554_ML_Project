    def create_order(self, is_ask, price, price_type, quantity, quantity_type):
        """
        Create a new ask or bid order.
        """
        asset1_amount = long(quantity * (10 ** self.wallets[quantity_type]["precision"]))

        price_num = price * (10 ** self.wallets[price_type]["precision"])
        price_denom = float(10 ** self.wallets[quantity_type]["precision"])
        price = price_num / price_denom

        asset2_amount = long(float(asset1_amount) / price)

        post_data = str("first_asset_amount=%d&first_asset_type=%s&second_asset_amount=%d&second_asset_type=%s" %
                        (asset1_amount, quantity_type, asset2_amount, price_type))
        self.request_mgr = TriblerRequestManager()
        self.request_mgr.perform_request("market/%s" % ('asks' if is_ask else 'bids'),
                                         lambda response: self.on_order_created(response, is_ask),
                                         data=post_data, method='PUT')