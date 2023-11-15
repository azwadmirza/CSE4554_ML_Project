def _truncate(kind, units):
    def truncator(translator, expr):
        op = expr.op()
        arg, unit = op.args

        arg = translator.translate(op.args[0])
        try:
            unit = units[unit]
        except KeyError:
            raise com.UnsupportedOperationError(
                '{!r} unit is not supported in timestamp truncate'.format(unit)
            )

        return "{}_TRUNC({}, {})".format(kind, arg, unit)
    return truncator