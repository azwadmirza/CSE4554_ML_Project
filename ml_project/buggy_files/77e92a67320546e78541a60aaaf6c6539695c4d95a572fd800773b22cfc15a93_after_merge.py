def data_processor(df, logger):
    """
    Takes a dataframe and logging instance as input.
    Checks for new generation types and logs awarning if any are found.
    Parses the dataframe row by row removing unneeded keys.
    Returns a list of 2 element tuples, each containing a datetime object
    and production dictionary.
    """

    # Remove leading whitespace in column headers.
    df.columns = df.columns.str.strip()

    keys_to_remove = {'GMT MKT Interval', 'Average Actual Load', 'Other', 'Waste Heat'}

    # Check for new generation columns.
    known_keys = MAPPING.keys() | keys_to_remove
    column_headers = set(df.columns)

    unknown_keys = column_headers - known_keys

    for heading in unknown_keys:
        logger.warning('New column \'{}\' present in US-SPP data source.'.format(
            heading), extra={'key': 'US-SPP'})

    keys_to_remove = keys_to_remove | unknown_keys

    processed_data = []
    for index, row in df.iterrows():
        production = row.to_dict()

        extra_unknowns = sum([production[k] for k in unknown_keys])
        production['unknown'] = production['Other'] + production['Waste Heat'] + extra_unknowns

        dt_aware = parser.parse(production['GMT MKT Interval'])

        for k in keys_to_remove:
            production.pop(k, None)

        mapped_production = {MAPPING.get(k,k):v for k,v in production.items()}

        processed_data.append((dt_aware, mapped_production))

    return processed_data