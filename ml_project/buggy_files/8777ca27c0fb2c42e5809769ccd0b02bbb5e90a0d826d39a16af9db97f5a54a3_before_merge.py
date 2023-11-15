def __virtual__():
    if not HAS_INFLUXDB:
        return False
    return __virtualname__