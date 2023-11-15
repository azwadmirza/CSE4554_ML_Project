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

    result = rlk_jsonloads_dict(response.text)
    if result['error']:
        if isinstance(result['error'], list):
            error = result['error'][0]
        else:
            error = result['error']

        if 'Rate limit exceeded' in error:
            log.debug(f'Kraken: Got rate limit exceeded error: {error}')
            return 'Rate limited exceeded'
        else:
            raise RemoteError(error)

    return result['result']