    def is_valid_tx(tx):
        """
        Verify whether a dictionary that contains a transaction, is valid.
        """
        required_fields = ['trader_id', 'order_number', 'partner_trader_id', 'partner_order_number',
                           'transaction_number', 'assets', 'transferred', 'timestamp', 'payment_complete', 'status']
        if not MarketBlock.has_fields(required_fields, tx):
            return False
        if len(tx) != len(required_fields):
            return False

        required_types = [('trader_id', str), ('order_number', int), ('partner_trader_id', str),
                          ('partner_order_number', int), ('transaction_number', int), ('assets', dict),
                          ('transferred', dict), ('timestamp', float), ('payment_complete', bool), ('status', str)]

        if not MarketBlock.is_valid_trader_id(tx['trader_id']) or not \
                MarketBlock.is_valid_trader_id(tx['partner_trader_id']):
            return False
        if not MarketBlock.is_valid_asset_pair(tx['assets']):
            return False
        if not MarketBlock.is_valid_asset_pair(tx['transferred']):
            return False
        if not MarketBlock.has_required_types(required_types, tx):
            return False

        return True