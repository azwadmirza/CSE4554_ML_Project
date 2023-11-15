    def free_tensor_data(self, tensor_key):
        from .operand import OperandActor
        tiled_tensor = self._get_tensor_by_key(tensor_key)
        for chunk in tiled_tensor.chunks:
            op_uid = OperandActor.gen_uid(self._session_id, chunk.op.key)
            scheduler_addr = self.get_scheduler(op_uid)
            op_ref = self.ctx.actor_ref(op_uid, address=scheduler_addr)
            op_ref.free_data(_tell=True)