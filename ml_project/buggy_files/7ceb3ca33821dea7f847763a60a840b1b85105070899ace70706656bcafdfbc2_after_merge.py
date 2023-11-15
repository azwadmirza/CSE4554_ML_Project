    def decompress_payload(self, raw_payload: bytes) -> bytes:
        # Do the Snappy Decompression only if Snappy Compression is supported by the protocol
        if self.snappy_support:
            try:
                return snappy.decompress(raw_payload)
            except Exception as err:
                # log this just in case it's a library error of some kind on valid messages.
                self.logger.debug("Snappy decompression error on payload: %s", raw_payload.hex())
                raise MalformedMessage from err
        else:
            return raw_payload