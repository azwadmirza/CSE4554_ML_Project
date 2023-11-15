    def _notify_buy(self, trade: Trade, order_type: str):
        """
        Sends rpc notification when a buy occured.
        """
        msg = {
            'type': RPCMessageType.BUY_NOTIFICATION,
            'exchange': self.exchange.name.capitalize(),
            'pair': trade.pair,
            'limit': trade.open_rate,
            'order_type': order_type,
            'stake_amount': trade.stake_amount,
            'stake_currency': self.config['stake_currency'],
            'fiat_currency': self.config.get('fiat_display_currency', None),
        }

        # Send the message
        self.rpc.send_msg(msg)