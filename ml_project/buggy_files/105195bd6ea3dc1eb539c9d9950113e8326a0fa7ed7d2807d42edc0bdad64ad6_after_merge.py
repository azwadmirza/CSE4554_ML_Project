    def create_operand_actors(self, _clean_io_meta=True, _start=True):
        """
        Create operand actors for all operands
        """
        logger.debug('Creating operand actors for graph %s', self._graph_key)

        chunk_graph = self.get_chunk_graph()
        operand_infos = self._operand_infos

        op_refs = dict()
        initial_keys = []
        for op_key in self._op_key_to_chunk:
            chunks = self._op_key_to_chunk[op_key]
            op = chunks[0].op

            op_name = type(op).__name__
            op_info = operand_infos[op_key]

            io_meta = self._collect_operand_io_meta(chunk_graph, chunks)
            op_info['op_name'] = op_name
            op_info['io_meta'] = io_meta

            if io_meta['predecessors']:
                state = 'UNSCHEDULED'
            else:
                initial_keys.append(op_key)
                state = 'READY'
            op_info['retries'] = 0
            op_info['state'] = state

            position = None
            if op_key in self._terminal_chunk_op_tensor:
                position = OperandPosition.TERMINAL
            elif not io_meta['predecessors']:
                position = OperandPosition.INITIAL

            op_cls = get_operand_actor_class(type(op))
            op_uid = op_cls.gen_uid(self._session_id, op_key)
            scheduler_addr = self.get_scheduler(op_uid)

            # if operand actor exists, the behavior depends on the existing operand state.
            op_ref = self.ctx.actor_ref(op_uid, address=scheduler_addr)
            if self.ctx.has_actor(op_ref):
                op_ref.append_graph(self._graph_key, op_info, position=position)
                op_refs[op_key] = op_ref
            else:
                op_refs[op_key] = self.ctx.create_actor(
                    op_cls, self._session_id, self._graph_key, op_key, op_info,
                    position=position, uid=op_uid, address=scheduler_addr, wait=False
                )

            op_info['state'] = getattr(OperandState, state.upper())
            if _clean_io_meta:
                del op_info['io_meta']

        self.state = GraphState.RUNNING

        if _start:
            op_refs = dict((k, v) if isinstance(v, ActorRef) else (k, v.result()) for k, v in op_refs.items())
            start_futures = [op_refs[op_key].start_operand(_tell=True, _wait=False)
                             for op_key in initial_keys]
            [future.result() for future in start_futures]