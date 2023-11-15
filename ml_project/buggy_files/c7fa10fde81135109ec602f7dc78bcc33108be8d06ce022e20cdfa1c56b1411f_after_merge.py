    def has_expired(self):
        """Check if the certificate has expired."""
        return datetime.datetime.now() > self._cert.not_valid_after