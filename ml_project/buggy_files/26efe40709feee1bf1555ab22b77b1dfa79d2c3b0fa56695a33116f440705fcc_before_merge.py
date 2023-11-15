    def __init__(self, data=None, secret_key=None, new=True):
        ModificationTrackingDict.__init__(self, data or ())
        # explicitly convert it into a bytestring because python 2.6
        # no longer performs an implicit string conversion on hmac
        if secret_key is not None:
            secret_key = to_bytes(secret_key, 'utf-8')
        self.secret_key = secret_key
        self.new = new