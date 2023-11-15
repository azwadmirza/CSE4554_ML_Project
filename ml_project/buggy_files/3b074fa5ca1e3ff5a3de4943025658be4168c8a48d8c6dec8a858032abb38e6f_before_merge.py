    def __init__(self, key):
        with reraise_errors('Invalid private key: {0!r}'):
            self._key = crypto.load_privatekey(crypto.FILETYPE_PEM, key)