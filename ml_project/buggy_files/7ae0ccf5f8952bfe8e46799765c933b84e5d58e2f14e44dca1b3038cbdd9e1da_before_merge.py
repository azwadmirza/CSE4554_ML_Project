    def set(self, key, value, state):
        """Store a value for a given key.

        Args:
              key: The key at which to store the value.
              value: The value to store.

        """
        key = bytes_to_str(key)
        LOGGER.debug("Creating CosmosDB document %s/%s/%s",
                     self._database_name, self._collection_name, key)

        self._client.CreateDocument(
            self._collection_link,
            {"id": key, "value": value},
            self._get_partition_key(key))