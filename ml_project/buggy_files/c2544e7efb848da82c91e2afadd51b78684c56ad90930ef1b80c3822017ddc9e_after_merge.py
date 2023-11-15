    def __init__(self, hostname: bytes, ctx, verify_certs: bool):
        self._ctx = ctx
        self._verifier = ConnectionVerifier(hostname, verify_certs)