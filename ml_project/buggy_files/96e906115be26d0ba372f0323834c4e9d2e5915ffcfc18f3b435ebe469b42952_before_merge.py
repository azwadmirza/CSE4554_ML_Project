    def _post_call_expression(self, expression):
        called = get(expression.called)
        args = [get(a) for a in expression.arguments if a]
        for arg in args:
            arg_ = Argument(arg)
            arg_.set_expression(expression)
            self._result.append(arg_)
        if isinstance(called, Function):
            # internal call

            # If tuple
            if expression.type_call.startswith('tuple(') and expression.type_call != 'tuple()':
                val = TupleVariable(self._node)
            else:
                val = TemporaryVariable(self._node)
            internal_call = InternalCall(called, len(args), val, expression.type_call)
            internal_call.set_expression(expression)
            self._result.append(internal_call)
            set_val(expression, val)
        else:
            # If tuple
            if expression.type_call.startswith('tuple(') and expression.type_call != 'tuple()':
                val = TupleVariable(self._node)
            else:
                val = TemporaryVariable(self._node)

            message_call = TmpCall(called, len(args), val, expression.type_call)
            message_call.set_expression(expression)
            # Gas/value are only accessible here if the syntax {gas: , value: }
            # Is used over .gas().value()
            if expression.call_gas:
                call_gas = get(expression.call_gas)
                message_call.call_gas = call_gas
            if expression.call_value:
                call_value = get(expression.call_value)
                message_call.call_value = call_value
            self._result.append(message_call)
            set_val(expression, val)