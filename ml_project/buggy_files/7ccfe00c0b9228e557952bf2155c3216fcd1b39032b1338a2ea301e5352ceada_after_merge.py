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

    # define the parameters
    params = OrderedDict()
    params['format'] = 'json'
    params['limit'] = 1
    params['dedupe'] = 0  # prevent OSM from deduping results so we get precisely 'limit' # of results
    params['q'] = query
    response_json = nominatim_request(params=params, timeout=30)

    # if results were returned, parse lat and long out of the result
    if len(response_json) > 0 and 'lat' in response_json[0] and 'lon' in response_json[0]:
        lat = float(response_json[0]['lat'])
        lon = float(response_json[0]['lon'])
        point = (lat, lon)
        log('Geocoded "{}" to {}'.format(query, point))
        return point
    else:
        raise Exception('Nominatim geocoder returned no results for query "{}"'.format(query))