    def __init__(self, hostname, ctx, verify_certs):
        self._ctx = ctx
        self._verifier = ConnectionVerifier(hostname, verify_certs)