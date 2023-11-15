    async def get(self, key):
        """Get data from Redis for a given key.

        Args:
            key (string): The key to lookup in the database.

        Returns:
            object or None: The data object stored for that key, or None if no
                            object found for that key.

        """
        if self.client:
            _LOGGER.debug(_("Getting %s from Redis."), key)
            data = await self.client.execute("GET", key)

            if data:
                return json.loads(data, object_hook=JSONDecoder())

            return None