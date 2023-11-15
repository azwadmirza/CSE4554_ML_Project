    def __init__(self, regr, key, meta=None):
        self.key = key
        self.regr = regr
        self.meta = self.Meta(
            # pyrfc3339 drops microseconds, make sure __eq__ is sane
            creation_dt=datetime.datetime.now(
                tz=pytz.UTC).replace(microsecond=0),
            creation_host=socket.getfqdn()) if meta is None else meta

        self.id = hashlib.md5(
            self.key.key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo)
        ).hexdigest()