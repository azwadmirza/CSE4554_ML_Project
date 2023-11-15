    def get_issuer(self):
        """Return issuer (CA) as a string."""
        return ' '.join(x.value for x in self._cert.issuer)