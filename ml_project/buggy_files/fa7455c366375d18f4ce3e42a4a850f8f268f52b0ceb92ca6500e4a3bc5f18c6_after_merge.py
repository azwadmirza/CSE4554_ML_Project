    def free_data(self, state=OperandState.FREED):
        """
        Free output data of current operand
        :param state: target state
        """
        if self.state == OperandState.FREED:
            return
        if state == OperandState.CANCELLED:
            can_be_freed = True
        else:
            can_be_freed_states = [graph_ref.check_operand_can_be_freed(self._succ_keys) for
                                   graph_ref in self._graph_refs]
            if None in can_be_freed_states:
                can_be_freed = None
            else:
                can_be_freed = all(can_be_freed_states)
        if can_be_freed is None:
            self.ref().free_data(state, _delay=1, _tell=True)
            return
        elif not can_be_freed:
            return

        self.start_operand(state)

        endpoint_lists = self._chunk_meta_ref.batch_get_workers(self._session_id, self._chunks)
        futures = []
        for chunk_key, endpoints in zip(self._chunks, endpoint_lists):
            if endpoints is None:
                continue
            for ep in endpoints:
                futures.append((self._free_worker_data(ep, chunk_key), ep))

        dead_workers = []
        for f, ep in futures:
            try:
                with rewrite_worker_errors():
                    f.result()
            except WorkerDead:
                dead_workers.append(ep)

        if dead_workers:
            self._resource_ref.detach_dead_workers(list(dead_workers), _tell=True)
            self._assigned_workers.difference_update(dead_workers)

        self._chunk_meta_ref.batch_delete_meta(self._session_id, self._chunks, _tell=True)