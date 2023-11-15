def trim_tickerlist(tickerlist: List[Dict], timerange: Tuple[Tuple, int, int]) -> List[Dict]:
    if not tickerlist:
        return tickerlist

    stype, start, stop = timerange

    start_index = 0
    stop_index = len(tickerlist)

    if stype[0] == 'line':
        stop_index = start
    if stype[0] == 'index':
        start_index = start
    elif stype[0] == 'date':
        while tickerlist[start_index][0] < start * 1000:
            start_index += 1

    if stype[1] == 'line':
        start_index = len(tickerlist) + stop
    if stype[1] == 'index':
        stop_index = stop
    elif stype[1] == 'date':
        while tickerlist[stop_index-1][0] > stop * 1000:
            stop_index -= 1

    if start_index > stop_index:
        raise ValueError(f'The timerange [{start},{stop}] is incorrect')

    return tickerlist[start_index:stop_index]