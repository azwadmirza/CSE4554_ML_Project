def trim_tickerlist(tickerlist: List[Dict], timerange: Tuple[Tuple, int, int]) -> List[Dict]:
    stype, start, stop = timerange
    if stype == (None, 'line'):
        return tickerlist[stop:]
    elif stype == ('line', None):
        return tickerlist[0:start]
    elif stype == ('index', 'index'):
        return tickerlist[start:stop]

    return tickerlist