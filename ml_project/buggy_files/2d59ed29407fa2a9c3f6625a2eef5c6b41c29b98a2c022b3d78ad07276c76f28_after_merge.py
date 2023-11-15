def read_and_validate_csv(path, delimiter=','):
    """Generator for reading a CSV file.

    Args:
        path: Path to the CSV file
        delimiter: character used as a field separator, default: ','
    """
    # Columns that must be present in the CSV file.
    mandatory_fields = ['message', 'datetime', 'timestamp_desc']

    # Ensures delimiter is a string.
    if not isinstance(delimiter, six.text_type):
        delimiter = codecs.decode(delimiter, 'utf8')

    # Due to issues with python2.
    if six.PY2:
        delimiter = str(delimiter)
        open_function = open(path, 'r')
    else:
        open_function = open(path, mode='r', encoding='utf-8')

    with open_function as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        csv_header = reader.fieldnames
        missing_fields = []
        # Validate the CSV header
        for field in mandatory_fields:
            if field not in csv_header:
                missing_fields.append(field)
        if missing_fields:
            raise RuntimeError(
                'Missing fields in CSV header: {0:s}'.format(
                    ','.join(missing_fields)))
        for row in reader:
            try:
                # normalize datetime to ISO 8601 format if it's not the case.
                parsed_datetime = parser.parse(row['datetime'])
                row['datetime'] = parsed_datetime.isoformat()

                normalized_timestamp = int(
                    time.mktime(parsed_datetime.utctimetuple()) * 1000000)
                normalized_timestamp += parsed_datetime.microsecond
                row['timestamp'] = str(normalized_timestamp)
            except ValueError:
                continue

            yield row