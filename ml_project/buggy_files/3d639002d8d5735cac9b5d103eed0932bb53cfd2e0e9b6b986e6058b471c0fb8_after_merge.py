    def set(self, key, value):
        """Set a key in Consul.

        Before creating the key it will create a session inside Consul
        where it creates a session with a TTL

        The key created afterwards will reference to the session's ID.

        If the session expires it will remove the key so that results
        can auto expire from the K/V store
        """
        session_name = bytes_to_str(key)

        key = self._key_to_consul_key(key)

        logger.debug('Trying to create Consul session %s with TTL %d',
                     session_name, self.expires)
        session_id = self.client.session.create(name=session_name,
                                                behavior='delete',
                                                ttl=self.expires)
        logger.debug('Created Consul session %s', session_id)

        logger.debug('Writing key %s to Consul', key)
        return self.client.kv.put(key=key,
                                  value=value,
                                  acquire=session_id)