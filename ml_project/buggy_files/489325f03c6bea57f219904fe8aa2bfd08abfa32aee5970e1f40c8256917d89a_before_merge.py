def fetch_PL():

    parameters = ["B01", "B02", "B03", "B04", "B05", "B06", "B10", "B11", "B12", "B19"]
    output_array = map(fetchValue, parameters)

    data = {
        'countryCode': COUNTRY_CODE,
        'production': {
            'wind': output_array[9],
            'solar': 0,
            'hydro': output_array[6] + output_array[7] + output_array[8],
            'biomass': output_array[0],
            'nuclear': 0,
            'gas': output_array[2] + output_array[3],
            'coal': output_array[1] + output_array[4],
            'oil': output_array[5],
            'unknown': 0
        }
    }

    return data