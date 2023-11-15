    def state(self, value):
        self._last_state = self._state
        if value != self._last_state:
            logger.debug('Operand %s(%s) state from %s to %s.', self._op_key, self._op_name,
                         self._last_state, value)
        self._state = value
        self._info['state'] = value.name
        futures = [
            self._graph_ref.set_operand_state(self._op_key, value.value, _tell=True, _wait=False),
        ]
        if self._kv_store_ref is not None:
            futures.append(self._kv_store_ref.write(
                '%s/state' % self._op_path, value.name, _tell=True, _wait=False))
        [f.result() for f in futures]