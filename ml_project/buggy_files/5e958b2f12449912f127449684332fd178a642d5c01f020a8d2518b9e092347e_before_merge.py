def file_dump_json(filename, data, is_zip=False) -> None:
    """
    Dump JSON data into a file
    :param filename: file to create
    :param data: JSON Data to save
    :return:
    """
    if is_zip:
        if not filename.endswith('.gz'):
            filename = filename + '.gz'
        with gzip.open(filename, 'w') as fp:
            json.dump(data, fp, default=str)
    else:
        with open(filename, 'w') as fp:
            json.dump(data, fp, default=str)