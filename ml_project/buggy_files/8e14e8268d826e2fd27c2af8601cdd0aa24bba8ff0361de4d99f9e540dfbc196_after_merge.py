    def stoploss_limit(self, pair: str, amount: float, stop_price: float, rate: float) -> Dict:
        """
        creates a stoploss limit order.
        NOTICE: it is not supported by all exchanges. only binance is tested for now.
        TODO: implementation maybe needs to be moved to the binance subclass
        """
        ordertype = "stop_loss_limit"

        stop_price = self.symbol_price_prec(pair, stop_price)

        # Ensure rate is less than stop price
        if stop_price <= rate:
            raise OperationalException(
                'In stoploss limit order, stop price should be more than limit price')

        if self._config['dry_run']:
            dry_order = self.dry_run_order(
                pair, ordertype, "sell", amount, stop_price)
            return dry_order

        params = self._params.copy()
        params.update({'stopPrice': stop_price})

        order = self.create_order(pair, ordertype, 'sell', amount, rate, params)
        logger.info('stoploss limit order added for %s. '
                    'stop price: %s. limit: %s', pair, stop_price, rate)
        return order