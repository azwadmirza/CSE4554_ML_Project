    def opportunistically_fill_in_missing_info_from_device(self, client: 'HardwareClientBase'):
        assert client is not None
        if self._root_fingerprint is None:
            self._root_fingerprint = client.request_root_fingerprint_from_device()
            self.is_requesting_to_be_rewritten_to_wallet_file = True
        if self.label != client.label():
            self.label = client.label()
            self.is_requesting_to_be_rewritten_to_wallet_file = True