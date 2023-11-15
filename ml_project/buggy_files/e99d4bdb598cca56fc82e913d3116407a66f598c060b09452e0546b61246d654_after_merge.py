    def _rpc_forcesell(self, trade_id) -> Dict[str, str]:
        """
        Handler for forcesell <id>.
        Sells the given trade at current price
        """
        def _exec_forcesell(trade: Trade) -> None:
            # Check if there is there is an open order
            if trade.open_order_id:
                order = self._freqtrade.exchange.get_order(trade.open_order_id, trade.pair)

                # Cancel open LIMIT_BUY orders and close trade
                if order and order['status'] == 'open' \
                        and order['type'] == 'limit' \
                        and order['side'] == 'buy':
                    self._freqtrade.exchange.cancel_order(trade.open_order_id, trade.pair)
                    trade.close(order.get('price') or trade.open_rate)
                    # Do the best effort, if we don't know 'filled' amount, don't try selling
                    if order['filled'] is None:
                        return
                    trade.amount = order['filled']

                # Ignore trades with an attached LIMIT_SELL order
                if order and order['status'] == 'open' \
                        and order['type'] == 'limit' \
                        and order['side'] == 'sell':
                    return

            # Get current rate and execute sell
            current_rate = self._freqtrade.get_sell_rate(trade.pair, False)
            self._freqtrade.execute_sell(trade, current_rate, SellType.FORCE_SELL)
        # ---- EOF def _exec_forcesell ----

        if self._freqtrade.state != State.RUNNING:
            raise RPCException('trader is not running')

        if trade_id == 'all':
            # Execute sell for all open orders
            for trade in Trade.get_open_trades():
                _exec_forcesell(trade)
            Trade.session.flush()
            return {'result': 'Created sell orders for all open trades.'}

        # Query for trade
        trade = Trade.get_trades(
            trade_filter=[Trade.id == trade_id, Trade.is_open.is_(True), ]
        ).first()
        if not trade:
            logger.warning('forcesell: Invalid argument received')
            raise RPCException('invalid argument')

        _exec_forcesell(trade)
        Trade.session.flush()
        return {'result': f'Created sell order for trade {trade_id}.'}