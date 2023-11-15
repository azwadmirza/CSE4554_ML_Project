def __virtual__():
    if HAS_TWILIO:
        return __virtualname__

    return False, 'Could not import sms returner; twilio is not installed.'