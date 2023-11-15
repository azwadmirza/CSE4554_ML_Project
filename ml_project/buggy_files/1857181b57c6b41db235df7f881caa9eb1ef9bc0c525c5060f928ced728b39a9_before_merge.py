    def _post_new_contract(self, expression):
        val = TemporaryVariable(self._node)
        operation = TmpNewContract(expression.contract_name, val)
        operation.set_expression(expression)
        self._result.append(operation)
        set_val(expression, val)