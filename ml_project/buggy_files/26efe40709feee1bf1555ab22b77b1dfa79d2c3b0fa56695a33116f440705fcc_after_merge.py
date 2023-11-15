    def __init__(self, data=None, secret_key=None, new=True):
        ModificationTrackingDict.__init__(self, data or ())
        # explicitly convert it into a bytestring because python 2.6
        # no longer performs an implicit string conversion on hmac
        if secret_key is not None:
            secret_key = to_bytes(secret_key, 'utf-8')
        self.secret_key = secret_key
        self.new = new

        if self.serialization_method is pickle:
            warnings.warn(
                'The default SecureCookie.serialization_method will change from pickle'
                ' to json in 1.0. To upgrade existing tokens, override unquote to try'
                ' pickle if json fails.'
            )