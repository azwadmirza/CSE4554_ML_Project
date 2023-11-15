def df_to_data(zone_key, day, df, logger):
    df = df.dropna(axis=1, how='any')
    # Check for empty dataframe
    if df.shape == (1, 1):
        return []
    df = df.drop(['Intercambio Sur', 'Intercambio Norte', 'Total'], errors='ignore')
    df = df.iloc[:, :-1]

    results = []
    unknown_plants = set()
    hour = 0
    for column in df:
        data = empty_record(zone_key)
        data_time = day.replace(hour=hour, minute=0, second=0, microsecond=0).datetime
        for index, value in df[column].items():
            source = POWER_PLANTS.get(index)
            if not source:
                source = 'unknown'
                unknown_plants.add(index)
            data['datetime'] = data_time
            data['production'][source] += max(0.0, value)
        hour += 1
        results.append(data)

    for plant in unknown_plants:
        logger.warning('{} is not mapped to generation type'.format(plant),
                       extra={'key': zone_key})

    return results