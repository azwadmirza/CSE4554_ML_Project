def _check_and_get_response(response: Response, method: str) -> Union[str, Dict]:
    """Checks the kraken response and if it's succesfull returns the result.

    If there is recoverable error a string is returned explaining the error
    May raise:
    - RemoteError if there is an unrecoverable/unexpected remote error
    """
    if response.status_code in (520, 525, 504):
        log.debug(f'Kraken returned status code {response.status_code}')
        return 'Usual kraken 5xx shenanigans'
    elif response.status_code != 200:
        raise RemoteError(
            'Kraken API request {} for {} failed with HTTP status '
            'code: {}'.format(
                response.url,
                method,
                response.status_code,
            ))

    try:
        decoded_json = rlk_jsonloads_dict(response.text)
    except json.decoder.JSONDecodeError as e:
        raise RemoteError(f'Invalid JSON in Kraken response. {e}')

    try:
        if decoded_json['error']:
            if isinstance(decoded_json['error'], list):
                error = decoded_json['error'][0]
            else:
                error = decoded_json['error']

            if 'Rate limit exceeded' in error:
                log.debug(f'Kraken: Got rate limit exceeded error: {error}')
                return 'Rate limited exceeded'
            else:
                raise RemoteError(error)

        result = decoded_json['result']
    except KeyError as e:
        raise RemoteError(f'Unexpected format of Kraken response. Missing key: {e}')

    return result