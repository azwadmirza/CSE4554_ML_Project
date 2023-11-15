def is_exchange_known_ccxt(exchange_name: str, ccxt_module=None) -> bool:
    return exchange_name in ccxt_exchanges(ccxt_module)