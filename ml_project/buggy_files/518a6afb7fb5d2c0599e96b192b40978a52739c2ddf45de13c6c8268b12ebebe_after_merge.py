    def _gen_pair_whitelist(self, pairlist: List[str], tickers: Dict,
                            base_currency: str, key: str, min_val: int) -> List[str]:
        """
        Updates the whitelist with with a dynamically generated list
        :param base_currency: base currency as str
        :param key: sort key (defaults to 'quoteVolume')
        :param tickers: Tickers (from exchange.get_tickers()).
        :return: List of pairs
        """

        if self._pairlist_pos == 0:
            # If VolumePairList is the first in the list, use fresh pairlist
            # check length so that we make sure that '/' is actually in the string
            filtered_tickers = [v for k, v in tickers.items()
                                if (len(k.split('/')) == 2 and k.split('/')[1] == base_currency
                                    and v[key] is not None)]
        else:
            # If other pairlist is in front, use the incomming pairlist.
            filtered_tickers = [v for k, v in tickers.items() if k in pairlist]

        if min_val > 0:
            filtered_tickers = list(filter(lambda t: t[key] > min_val, filtered_tickers))

        sorted_tickers = sorted(filtered_tickers, reverse=True, key=lambda t: t[key])

        # Validate whitelist to only have active market pairs
        pairs = self._whitelist_for_active_markets([s['symbol'] for s in sorted_tickers])
        pairs = self._verify_blacklist(pairs)
        # Limit to X number of pairs
        pairs = pairs[:self._number_pairs]
        logger.info(f"Searching {self._number_pairs} pairs: {pairs}")

        return pairs