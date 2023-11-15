def save_csv(data_fp, data):
    with open(data_fp, 'w', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        for row in data:
            if not isinstance(row, collections.Iterable) or isinstance(row, str):
                row = [row]
            writer.writerow(row)