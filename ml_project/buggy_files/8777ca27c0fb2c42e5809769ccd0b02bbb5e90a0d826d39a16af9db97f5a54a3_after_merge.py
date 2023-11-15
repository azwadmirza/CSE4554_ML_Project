def __virtual__():
    if not HAS_INFLUXDB:
        return False, 'Could not import influxdb returner; ' \
                      'influxdb python client is not installed.'
    return __virtualname__