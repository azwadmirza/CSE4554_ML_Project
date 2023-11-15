    def __init__(self, cert):
        assert crypto is not None
        with reraise_errors('Invalid certificate: {0!r}'):
            self._cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert)