    def server_sni(self):
        """
        The Server Name Indication we want to send with the next server TLS handshake.
        """
        if self._custom_server_sni is False:
            return None
        else:
            return self._custom_server_sni or self._client_hello.sni