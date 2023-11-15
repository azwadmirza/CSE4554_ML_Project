    def has_expired(self):
        """Check if the certificate has expired."""
        return self._cert.has_expired()