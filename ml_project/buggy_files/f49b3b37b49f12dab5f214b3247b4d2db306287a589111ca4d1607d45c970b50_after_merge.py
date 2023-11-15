    def getfullargspec(func):
        return getargspec(func) + ([], None, {})