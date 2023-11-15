def __virtual__():
    if not has_raven:
        return False, 'Could not import sentry returner; ' \
                      'raven python client is not installed.'
    return __virtualname__