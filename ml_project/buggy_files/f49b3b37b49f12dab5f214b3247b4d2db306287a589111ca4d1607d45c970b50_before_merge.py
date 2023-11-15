    def getfullargspec(func):
        return getargspec(unwrap(func)) + ([], None, {})