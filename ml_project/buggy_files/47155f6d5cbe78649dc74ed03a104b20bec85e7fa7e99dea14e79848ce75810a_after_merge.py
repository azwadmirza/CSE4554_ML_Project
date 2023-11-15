    def get_operand_states(self, op_keys):
        return [self._operand_infos[k]['state'] for k in op_keys if k in self._operand_infos]