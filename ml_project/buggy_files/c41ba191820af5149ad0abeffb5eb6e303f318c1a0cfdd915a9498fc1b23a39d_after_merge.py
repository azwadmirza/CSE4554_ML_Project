    def copy_expression(self, expression, true_expression, false_expression):
        if self.condition:
            return

        if isinstance(expression, ConditionalExpression):
             raise Exception('Nested ternary operator not handled')

        if isinstance(expression, (Literal, Identifier, IndexAccess, NewArray, NewContract)):
            return None

        # case of lib
        # (.. ? .. : ..).add
        if isinstance(expression, MemberAccess):
            next_expr = expression.expression
            if self.apply_copy(next_expr, true_expression, false_expression, f_expression):
                self.copy_expression(next_expr,
                                     true_expression.expression,
                                     false_expression.expression)

        elif isinstance(expression, (AssignmentOperation, BinaryOperation, TupleExpression)):
            true_expression._expressions = []
            false_expression._expressions = []

            for next_expr in expression.expressions:
                if self.apply_copy(next_expr, true_expression, false_expression, f_expressions):
                    # always on last arguments added
                    self.copy_expression(next_expr,
                                         true_expression.expressions[-1],
                                         false_expression.expressions[-1])

        elif isinstance(expression, CallExpression):
            next_expr = expression.called

            # case of lib
            # (.. ? .. : ..).add
            if self.apply_copy(next_expr, true_expression, false_expression, f_called):
                self.copy_expression(next_expr,
                                     true_expression.called,
                                     false_expression.called)

            true_expression._arguments = []
            false_expression._arguments = []

            for next_expr in expression.arguments:
                if self.apply_copy(next_expr, true_expression, false_expression, f_call):
                    # always on last arguments added
                    self.copy_expression(next_expr,
                                         true_expression.arguments[-1],
                                         false_expression.arguments[-1])

        elif isinstance(expression, TypeConversion):
            next_expr = expression.expression
            if self.apply_copy(next_expr, true_expression, false_expression, f_expression):
                self.copy_expression(expression.expression,
                                     true_expression.expression,
                                     false_expression.expression)

        else:
            raise Exception('Ternary operation not handled {}({})'.format(expression, type(expression)))