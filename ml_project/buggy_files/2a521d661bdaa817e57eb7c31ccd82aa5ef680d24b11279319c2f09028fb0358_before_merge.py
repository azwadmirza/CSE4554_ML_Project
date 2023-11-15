def get_data(session=None):
    """ Returns generation data as a list of floats."""

    s = session or requests.Session()

    data_response = s.get(data_url)
    raw_data = data_response.text

    data = [float(i) for i in raw_data.split(',')]

    return data