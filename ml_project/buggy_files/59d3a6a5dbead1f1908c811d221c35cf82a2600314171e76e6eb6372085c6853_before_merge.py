def symbol_is_pair(market_symbol: str, base_currency: str = None, quote_currency: str = None):
    """
    Check if the market symbol is a pair, i.e. that its symbol consists of the base currency and the
    quote currency separated by '/' character. If base_currency and/or quote_currency is passed,
    it also checks that the symbol contains appropriate base and/or quote currency part before
    and after the separating character correspondingly.
    """
    symbol_parts = market_symbol.split('/')
    return (len(symbol_parts) == 2 and
            (symbol_parts[0] == base_currency if base_currency else len(symbol_parts[0]) > 0) and
            (symbol_parts[1] == quote_currency if quote_currency else len(symbol_parts[1]) > 0))