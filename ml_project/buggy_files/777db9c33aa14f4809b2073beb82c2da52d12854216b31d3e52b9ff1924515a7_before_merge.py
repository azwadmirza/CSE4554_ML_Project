    def convert_to_ssl(self, *args, **kwargs):
        super().convert_to_ssl(*args, **kwargs)
        self.timestamp_ssl_setup = time.time()
        self.sni = self.connection.get_servername()
        self.cipher_name = self.connection.get_cipher_name()
        self.tls_version = self.connection.get_protocol_version_name()