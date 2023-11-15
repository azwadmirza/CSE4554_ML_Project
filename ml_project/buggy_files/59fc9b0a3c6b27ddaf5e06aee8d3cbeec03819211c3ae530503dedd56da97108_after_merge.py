    def process_compressed_mdblob(self, compressed_data):
        try:
            decompressed_data = lz4.frame.decompress(compressed_data)
        except RuntimeError:
            self._logger.warning("Unable to decompress mdblob")
            return []

        return self.process_squashed_mdblob(decompressed_data)