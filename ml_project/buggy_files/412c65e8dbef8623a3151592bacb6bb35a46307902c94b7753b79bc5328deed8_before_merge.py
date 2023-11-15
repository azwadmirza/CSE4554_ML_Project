    def dm_func(denom):
        max_num = max_value * denom if max_value is not None else None
        min_num = min_value * denom if min_value is not None else None

        return builds(
            Fraction,
            integers(min_value=min_num, max_value=max_num),
            just(denom)
        )