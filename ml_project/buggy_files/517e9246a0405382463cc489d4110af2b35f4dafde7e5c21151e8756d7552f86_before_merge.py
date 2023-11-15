    def _post_index_access(self, expression):
        left = get(expression.expression_left)
        right = get(expression.expression_right)
        val = ReferenceVariable(self._node)
        operation = Index(val, left, right, expression.type)
        self._result.append(operation)
        set_val(expression, val)