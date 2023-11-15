    def __init__(self, cert):
        with reraise_errors(
            'Invalid certificate: {0!r}', errors=(ValueError,)
        ):
            self._cert = load_pem_x509_certificate(
                ensure_bytes(cert), backend=default_backend())