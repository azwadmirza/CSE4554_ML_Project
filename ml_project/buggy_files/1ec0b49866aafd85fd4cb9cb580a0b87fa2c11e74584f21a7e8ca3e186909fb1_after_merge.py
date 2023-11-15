    def check_operand_can_be_freed(self, succ_op_keys):
        """
        Check if the data of an operand can be freed.

        :param succ_op_keys: keys of successor operands
        :return: True if can be freed, False if cannot. None when the result
                 is not determinant and we need to test later.
        """
        operand_infos = self._operand_infos
        for k in succ_op_keys:
            if k not in operand_infos:
                continue
            op_info = operand_infos[k]
            op_state = op_info.get('state')
            if op_state not in OperandState.SUCCESSFUL_STATES:
                return False
            failover_state = op_info.get('failover_state')
            if failover_state and failover_state not in OperandState.SUCCESSFUL_STATES:
                return False
        # if can be freed but blocked by an ongoing fail-over step,
        # we try later.
        if self._operand_free_paused:
            return None
        return True