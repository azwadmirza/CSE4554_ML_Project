    def _notify_buy(self, trade: Trade, order_type: str) -> None:
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
            'amount': trade.amount,
            'open_date': trade.open_date or datetime.utcnow(),
            'current_rate': trade.open_rate_requested,
        }

        # Send the message
        self.rpc.send_msg(msg)