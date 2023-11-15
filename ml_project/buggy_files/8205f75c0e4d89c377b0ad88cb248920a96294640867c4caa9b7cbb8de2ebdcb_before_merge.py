    def stop_graph(self):
        """
        Stop graph execution
        """
        from .operand import OperandActor
        if self.state == GraphState.CANCELLED:
            return
        self.state = GraphState.CANCELLING

        try:
            chunk_graph = self.get_chunk_graph()
        except (KeyError, GraphNotExists):
            self.state = GraphState.CANCELLED
            return

        for chunk in chunk_graph:
            if chunk.op.key not in self._operand_infos:
                continue
            if self._operand_infos[chunk.op.key]['state'] in \
                    (OperandState.READY, OperandState.RUNNING, OperandState.FINISHED):
                # we only need to stop on ready, running and finished operands
                op_uid = OperandActor.gen_uid(self._session_id, chunk.op.key)
                scheduler_addr = self.get_scheduler(op_uid)
                ref = self.ctx.actor_ref(op_uid, address=scheduler_addr)
                ref.stop_operand(_tell=True)