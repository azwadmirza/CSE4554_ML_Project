    def __init__(self, key=None, cert=None, cert_store=None,
                 digest=DEFAULT_SECURITY_DIGEST, serializer='json'):
        self._key = key
        self._cert = cert
        self._cert_store = cert_store
        self._digest = get_digest_algorithm(digest)
        self._serializer = serializer