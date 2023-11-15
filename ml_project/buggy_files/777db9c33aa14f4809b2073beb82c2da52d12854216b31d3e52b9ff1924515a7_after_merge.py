    def convert_to_ssl(self, *args, **kwargs):
        super().convert_to_ssl(*args, **kwargs)
        self.timestamp_ssl_setup = time.time()
        sni = self.connection.get_servername()
        if sni:
            self.sni = sni.decode("idna")
        else:
            self.sni = None
        self.cipher_name = self.connection.get_cipher_name()
        self.tls_version = self.connection.get_protocol_version_name()