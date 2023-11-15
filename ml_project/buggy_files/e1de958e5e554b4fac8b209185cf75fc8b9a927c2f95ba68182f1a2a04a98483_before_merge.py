    def verify(self, data, signature, digest):
        """Verify signature for string containing data."""
        with reraise_errors('Bad signature: {0!r}'):
            crypto.verify(self._cert, signature, data, digest)