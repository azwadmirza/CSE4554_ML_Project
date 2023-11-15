    def __init__(self, name, value, path=None, domain=None, secure=False,
                 httpOnly=False, expiry=None):
        self.name = name
        self.value = value
        self.path = path
        self.domain = domain
        self.secure = secure
        self.httpOnly = httpOnly
        self.expiry = datetime.fromtimestamp(expiry) if expiry else None