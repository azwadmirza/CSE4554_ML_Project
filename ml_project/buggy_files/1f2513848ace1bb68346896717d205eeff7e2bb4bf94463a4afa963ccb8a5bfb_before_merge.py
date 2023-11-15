    def _add_object(self, obj_type, data, timestamp=None):
        if timestamp is None:
            timestamp = self.stop_timestamp or time.time()
        if self.start_timestamp is None:
            self.start_timestamp = timestamp
        self.stop_timestamp = timestamp
        timestamp = int((timestamp - self.start_timestamp) * 1e9)
        obj_size = HEADER_SIZE + len(data)
        base_header = OBJ_HEADER_BASE_STRUCT.pack(
            b"LOBJ", HEADER_SIZE, 1, obj_size, obj_type)
        obj_header = OBJ_HEADER_STRUCT.pack(2, 0, 0, max(timestamp, 0))

        self.cache.append(base_header)
        self.cache.append(obj_header)
        self.cache.append(data)
        padding_size = len(data) % 4
        if padding_size:
            self.cache.append(b"\x00" * padding_size)

        self.cache_size += obj_size + padding_size
        self.count_of_objects += 1
        if self.cache_size >= self.MAX_CACHE_SIZE:
            self._flush()