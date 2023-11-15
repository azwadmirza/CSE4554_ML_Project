def _map_request_error(exc: RequestError, key: str):
    '''Map RequestError to more general exception if possible'''

    if exc.code == 404 and key:
        return NoSuchObject(key)
    elif exc.message == 'Forbidden':
        return AuthorizationError(exc.message)
    elif exc.message in ('Login Required', 'Invalid Credentials'):
        return AuthenticationError(exc.message)

    return None