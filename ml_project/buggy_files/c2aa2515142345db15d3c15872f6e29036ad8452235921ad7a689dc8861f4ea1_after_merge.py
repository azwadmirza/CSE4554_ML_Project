def _load_stock(filename):
    data = {
        'date' : [],
        'open' : [],
        'high' : [],
        'low' : [],
        'close' : [],
        'volume' : [],
        'adj_close': [],
    }
    with _open_csv_file(filename) as f:
        next(f)
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            date, open_price, high, low, close, volume, adj_close = row
            data['date'].append(date)
            data['open'].append(float(open_price))
            data['high'].append(float(high))
            data['low'].append(float(low))
            data['close'].append(float(close))
            data['volume'].append(int(volume))
            data['adj_close'].append(float(adj_close))
    return data