def geocode(query):
    """
    Geocode a query string to (lat, lon) with the Nominatim geocoder.

    Parameters
    ----------
    query : string
        the query string to geocode

    Returns
    -------
    point : tuple
        the (lat, lon) coordinates returned by the geocoder
    """

    # send the query to the nominatim geocoder and parse the json response
    url_template = 'https://nominatim.openstreetmap.org/search?format=json&limit=1&q={}'
    url = url_template.format(query)
    response = requests.get(url, timeout=60)
    results = response.json()

    # if results were returned, parse lat and long out of the result
    if len(results) > 0 and 'lat' in results[0] and 'lon' in results[0]:
        lat = float(results[0]['lat'])
        lon = float(results[0]['lon'])
        point = (lat, lon)
        log('Geocoded "{}" to {}'.format(query, point))
        return point
    else:
        raise Exception('Nominatim geocoder returned no results for query "{}"'.format(query))