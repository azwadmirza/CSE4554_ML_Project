    def _whitelist_for_active_markets(self, pairlist: List[str]) -> List[str]:
        """
        Check available markets and remove pair from whitelist if necessary
        :param whitelist: the sorted list of pairs the user might want to trade
        :return: the list of pairs the user wants to trade without those unavailable or
        black_listed
        """
        markets = self._exchange.markets
        if not markets:
            raise OperationalException(
                    'Markets not loaded. Make sure that exchange is initialized correctly.')

        sanitized_whitelist: List[str] = []
        for pair in pairlist:
            # pair is not in the generated dynamic market or has the wrong stake currency
            if pair not in markets:
                logger.warning(f"Pair {pair} is not compatible with exchange "
                               f"{self._exchange.name}. Removing it from whitelist..")
                continue

            if self._exchange.get_pair_quote_currency(pair) != self._config['stake_currency']:
                logger.warning(f"Pair {pair} is not compatible with your stake currency "
                               f"{self._config['stake_currency']}. Removing it from whitelist..")
                continue

            # Check if market is active
            market = markets[pair]
            if not market_is_active(market):
                logger.info(f"Ignoring {pair} from whitelist. Market is not active.")
                continue
            if pair not in sanitized_whitelist:
                sanitized_whitelist.append(pair)

        # We need to remove pairs that are unknown
        return sanitized_whitelist