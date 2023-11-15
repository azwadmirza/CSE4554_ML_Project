    def set(self, key, value):
        """Store a value for a given key.

        Args:
              key: The key at which to store the value.
              value: The value to store.

        """
        key = bytes_to_str(key)
        LOGGER.debug("Creating Azure Block Blob at %s/%s",
                     self._container_name, key)

        return self._client.create_blob_from_text(
            self._container_name, key, value)