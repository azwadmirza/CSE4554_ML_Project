    def _post_new_contract(self, expression):
        val = TemporaryVariable(self._node)
        operation = TmpNewContract(expression.contract_name, val)
        operation.set_expression(expression)
        if expression.call_value:
            call_value = get(expression.call_value)
            operation.call_value = call_value
        if expression.call_salt:
            call_salt = get(expression.call_salt)
            operation.call_salt = call_salt

        self._result.append(operation)
        set_val(expression, val)