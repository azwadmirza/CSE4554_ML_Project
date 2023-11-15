    def adjust(self, pairs) -> list:
        """
        Filters out and sorts "pairs" according to Edge calculated pairs
        """
        final = []
        for pair, info in self._cached_pairs.items():
            if info.expectancy > float(self.edge_config.get('minimum_expectancy', 0.2)) and \
                info.winrate > float(self.edge_config.get('minimum_winrate', 0.60)) and \
                    pair in pairs:
                final.append(pair)

        if self._final_pairs != final:
            self._final_pairs = final
            if self._final_pairs:
                logger.info(
                    'Minimum expectancy and minimum winrate are met only for %s,'
                    ' so other pairs are filtered out.',
                    self._final_pairs
                    )
            else:
                logger.info(
                    'Edge removed all pairs as no pair with minimum expectancy '
                    'and minimum winrate was found !'
                    )

        return self._final_pairs