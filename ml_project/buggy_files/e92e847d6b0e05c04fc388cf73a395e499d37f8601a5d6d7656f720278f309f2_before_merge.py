def save_csv(data_fp, data):
    writer = csv.writer(open(data_fp, 'w'))
    for row in data:
        if not isinstance(row, collections.Iterable) or isinstance(row, str):
            row = [row]
        writer.writerow(row)