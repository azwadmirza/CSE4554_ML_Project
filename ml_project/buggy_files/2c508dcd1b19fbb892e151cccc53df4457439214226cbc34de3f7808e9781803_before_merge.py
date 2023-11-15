    def set(self, key, value, state):
        body = {
            'result': value,
            '@timestamp': '{0}Z'.format(
                datetime.utcnow().isoformat()[:-3]
            ),
        }
        try:
            self._index(
                id=key,
                body=body,
            )
        except elasticsearch.exceptions.ConflictError:
            # document already exists, update it
            self._update(key, body, state)