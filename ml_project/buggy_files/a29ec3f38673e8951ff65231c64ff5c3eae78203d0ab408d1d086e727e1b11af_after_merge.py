    def _flush(self):
        """Compresses and writes data in the cache to file."""
        if self.fp.closed:
            return
        cache = b"".join(self.cache)
        if not cache:
            # Nothing to write
            return
        uncompressed_data = cache[:self.MAX_CACHE_SIZE]
        # Save data that comes after max size to next round
        tail = cache[self.MAX_CACHE_SIZE:]
        self.cache = [tail]
        self.cache_size = len(tail)
        compressed_data = zlib.compress(uncompressed_data,
                                        self.COMPRESSION_LEVEL)
        obj_size = (OBJ_HEADER_V1_STRUCT.size + LOG_CONTAINER_STRUCT.size +
                    len(compressed_data))
        base_header = OBJ_HEADER_BASE_STRUCT.pack(
            b"LOBJ", OBJ_HEADER_BASE_STRUCT.size, 1, obj_size, LOG_CONTAINER)
        container_header = LOG_CONTAINER_STRUCT.pack(
            ZLIB_DEFLATE, len(uncompressed_data))
        self.fp.write(base_header)
        self.fp.write(container_header)
        self.fp.write(compressed_data)
        # Write padding bytes
        self.fp.write(b"\x00" * (obj_size % 4))
        self.uncompressed_size += OBJ_HEADER_V1_STRUCT.size + LOG_CONTAINER_STRUCT.size
        self.uncompressed_size += len(uncompressed_data)