    def fetch_tensor_result(self, tensor_key):
        from ..worker.transfer import ResultSenderActor

        # TODO for test
        tiled_tensor = self._get_tensor_by_key(tensor_key)
        if tensor_key not in self._terminated_tensors:
            return None

        ctx = dict()
        for chunk_key in [c.key for c in tiled_tensor.chunks]:
            if chunk_key in ctx:
                continue
            endpoints = self._chunk_meta_ref.get_workers(self._session_id, chunk_key)
            sender_ref = self.ctx.actor_ref(ResultSenderActor.default_name(), address=endpoints[-1])
            ctx[chunk_key] = loads(sender_ref.fetch_data(self._session_id, chunk_key))
        return dumps(merge_tensor_chunks(tiled_tensor, ctx))