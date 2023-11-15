    def worker(self, value):
        futures =[]
        for graph_ref in self._graph_refs:
            futures.append(graph_ref.set_operand_worker(self._op_key, value, _tell=True, _wait=False))
        if self._kv_store_ref is not None:
            if value:
                futures.append(self._kv_store_ref.write(
                    '%s/worker' % self._op_path, value, _tell=True, _wait=False))
            elif self._worker is not None:
                futures.append(self._kv_store_ref.delete(
                    '%s/worker' % self._op_path, silent=True, _tell=True, _wait=False))
        [f.result() for f in futures]
        self._worker = value