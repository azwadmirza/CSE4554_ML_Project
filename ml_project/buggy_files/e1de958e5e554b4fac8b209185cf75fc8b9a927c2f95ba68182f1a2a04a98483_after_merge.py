    def verify(self, data, signature, digest):
        """Verify signature for string containing data."""
        with reraise_errors('Bad signature: {0!r}'):

            padd = padding.PSS(
                mgf=padding.MGF1(digest),
                salt_length=padding.PSS.MAX_LENGTH)

            self.get_pubkey().verify(signature,
                                     ensure_bytes(data), padd, digest)