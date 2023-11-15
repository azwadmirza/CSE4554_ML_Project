def _true_divide(t, expr):
    op = expr.op()
    left, right = op.args

    if util.all_of(op.args, ir.IntegerValue):
        new_expr = left.div(right.cast('double'))
        return t.translate(new_expr)

    return fixed_arity(lambda x, y: x / y, 2)(t, expr)