    def set_operand_worker(self, op_key, worker):
        op_info = self._operand_infos[op_key]
        if worker:
            op_info['worker'] = worker
        else:
            try:
                del op_info['worker']
            except KeyError:
                pass
        self._graph_meta_ref.update_op_worker(op_key, op_info['op_name'], worker,
                                              _tell=True, _wait=False)