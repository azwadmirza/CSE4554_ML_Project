    def get_issuer(self):
        """Return issuer (CA) as a string."""
        return ' '.join(bytes_to_str(x[1]) for x in
                        self._cert.get_issuer().get_components())