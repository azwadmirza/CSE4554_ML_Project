    def put_objects_by_keys(self, session_id, data_keys, shapes=None, pin_token=None):
        sizes = []
        for data_key in data_keys:
            buf = None
            try:
                buf = self._shared_store.get_buffer(session_id, data_key)
                size = len(buf)
                self._internal_put_object(session_id, data_key, buf, size)
            finally:
                del buf
            sizes.append(size)
        if pin_token:
            self.pin_data_keys(session_id, data_keys, pin_token)

        self._finish_put_objects(session_id, data_keys)
        self.storage_client.register_data(
            session_id, data_keys, (0, self._storage_device), sizes, shapes=shapes)