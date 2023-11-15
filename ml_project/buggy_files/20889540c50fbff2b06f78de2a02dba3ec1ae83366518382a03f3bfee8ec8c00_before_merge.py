    def sign(self, data, digest):
        """Sign string containing data."""
        with reraise_errors('Unable to sign data: {0!r}'):
            return crypto.sign(self._key, ensure_bytes(data), digest)