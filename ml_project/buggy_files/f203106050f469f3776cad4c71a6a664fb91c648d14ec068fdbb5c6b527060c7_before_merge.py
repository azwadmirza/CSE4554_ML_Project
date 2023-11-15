    def __init__(self, key=None, cert=None, cert_store=None,
                 digest='sha1', serializer='json'):
        self._key = key
        self._cert = cert
        self._cert_store = cert_store
        self._digest = bytes_if_py2(digest)
        self._serializer = serializer