def get_data(session=None):
    """ Returns generation data as a list of floats."""

    s = session or requests.Session()

    #In order for the data url to return data, cookies from the display url must be obtained then reused.
    response = s.get(display_url)
    data_response = s.get(data_url)
    raw_data = data_response.text
    data = [float(i) for i in raw_data.split(',')]

    return data