    def process_compressed_mdblob(self, compressed_data):
        return self.process_squashed_mdblob(lz4.frame.decompress(compressed_data))