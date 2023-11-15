def request_get(uri, timeout=ALL_REMOTES_TIMEOUT):
    response = requests.get(uri)
    if response.status_code != 200:
        raise RemoteError('Get {} returned status code {}'.format(uri, response.status_code))

    try:
        result = rlk_jsonloads(response.text)
    except json.decoder.JSONDecodeError:
        raise ValueError('{} returned malformed json'.format(uri))

    return result