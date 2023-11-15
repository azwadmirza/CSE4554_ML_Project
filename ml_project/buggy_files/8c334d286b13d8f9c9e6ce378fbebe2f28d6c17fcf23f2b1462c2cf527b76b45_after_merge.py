def register_auth(key=None, cert=None, store=None,
                  digest=DEFAULT_SECURITY_DIGEST,
                  serializer='json'):
    """Register security serializer."""
    s = SecureSerializer(key and PrivateKey(key),
                         cert and Certificate(cert),
                         store and FSCertStore(store),
                         digest, serializer=serializer)
    registry.register('auth', s.serialize, s.deserialize,
                      content_type='application/data',
                      content_encoding='utf-8')