def __virtual__():
    if HAS_TWILIO:
        return __virtualname__
    else:
        return False