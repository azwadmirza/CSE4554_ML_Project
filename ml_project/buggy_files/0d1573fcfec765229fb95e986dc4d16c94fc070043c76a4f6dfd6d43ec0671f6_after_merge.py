    def _visit_call_expression(self, expression):
        self._visit_expression(expression.called)
        for arg in expression.arguments:
            if arg:
                self._visit_expression(arg)
        if expression.call_value:
            self._visit_expression(expression.call_value)
        if expression.call_gas:
            self._visit_expression(expression.call_gas)
        if expression.call_salt:
            self._visit_expression(expression.call_salt)