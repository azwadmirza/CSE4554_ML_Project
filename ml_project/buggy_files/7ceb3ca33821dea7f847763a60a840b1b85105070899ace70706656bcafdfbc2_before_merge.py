    def decompress_payload(self, raw_payload: bytes) -> bytes:
        # Do the Snappy Decompression only if Snappy Compression is supported by the protocol
        if self.snappy_support:
            return snappy.decompress(raw_payload)
        else:
            return raw_payload