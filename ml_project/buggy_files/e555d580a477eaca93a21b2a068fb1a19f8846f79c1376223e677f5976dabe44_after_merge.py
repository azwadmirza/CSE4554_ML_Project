    def update_trade_state(self, trade: Trade, action_order: dict = None) -> None:
        """
        Checks trades with open orders and updates the amount if necessary
        """
        # Get order details for actual price per unit
        if trade.open_order_id:
            # Update trade with order values
            logger.info('Found open order for %s', trade)
            try:
                order = action_order or self.exchange.get_order(trade.open_order_id, trade.pair)
            except InvalidOrderException as exception:
                logger.warning('Unable to fetch order %s: %s', trade.open_order_id, exception)
                return
            # Try update amount (binance-fix)
            try:
                new_amount = self.get_real_amount(trade, order)
                if not isclose(order['amount'], new_amount, abs_tol=constants.MATH_CLOSE_PREC):
                    order['amount'] = new_amount
                    # Fee was applied, so set to 0
                    trade.fee_open = 0
                    trade.recalc_open_trade_price()

            except DependencyException as exception:
                logger.warning("Could not update trade amount: %s", exception)

            trade.update(order)

            # Updating wallets when order is closed
            if not trade.is_open:
                self.wallets.update()