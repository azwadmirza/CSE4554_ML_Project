def __virtual__():
    if not HAS_KAFKA:
        return False, 'Could not import kafka returner; kafka-python is not installed.'
    return __virtualname__