def register_auth(key=None, cert=None, store=None, digest='sha1',
                  serializer='json'):
    """Register security serializer."""
    s = SecureSerializer(key and PrivateKey(key),
                         cert and Certificate(cert),
                         store and FSCertStore(store),
                         digest=digest, serializer=serializer)
    registry.register('auth', s.serialize, s.deserialize,
                      content_type='application/data',
                      content_encoding='utf-8')