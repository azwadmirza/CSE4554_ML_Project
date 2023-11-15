    def handle_timedout_limit_buy(self, trade: Trade, order: Dict) -> bool:
        """
        Buy timeout - cancel order
        :return: True if order was fully cancelled
        """
        reason = "cancelled due to timeout"
        if order['status'] != 'canceled':
            corder = self.exchange.cancel_order(trade.open_order_id, trade.pair)
        else:
            # Order was cancelled already, so we can reuse the existing dict
            corder = order
            reason = "canceled on Exchange"

        if corder.get('remaining', order['remaining']) == order['amount']:
            # if trade is not partially completed, just delete the trade
            self.handle_buy_order_full_cancel(trade, reason)
            return True

        # if trade is partially complete, edit the stake details for the trade
        # and close the order
        # cancel_order may not contain the full order dict, so we need to fallback
        # to the order dict aquired before cancelling.
        # we need to fall back to the values from order if corder does not contain these keys.
        trade.amount = order['amount'] - corder.get('remaining', order['remaining'])
        trade.stake_amount = trade.amount * trade.open_rate
        # verify if fees were taken from amount to avoid problems during selling
        try:
            new_amount = self.get_real_amount(trade, corder if 'fee' in corder else order,
                                              trade.amount)
            if not isclose(order['amount'], new_amount, abs_tol=constants.MATH_CLOSE_PREC):
                trade.amount = new_amount
                # Fee was applied, so set to 0
                trade.fee_open = 0
        except DependencyException as e:
            logger.warning("Could not update trade amount: %s", e)

        trade.open_order_id = None
        logger.info('Partial buy order timeout for %s.', trade)
        self.rpc.send_msg({
            'type': RPCMessageType.STATUS_NOTIFICATION,
            'status': f'Remaining buy order for {trade.pair} cancelled due to timeout'
        })
        return False