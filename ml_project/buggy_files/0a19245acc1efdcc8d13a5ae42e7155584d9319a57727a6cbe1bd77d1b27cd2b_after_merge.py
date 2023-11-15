    def truncator(translator, expr):
        arg, unit = expr.op().args
        trans_arg = translator.translate(arg)
        valid_unit = units.get(unit)
        if valid_unit is None:
            raise com.UnsupportedOperationError(
                'BigQuery does not support truncating {} values to unit '
                '{!r}'.format(arg.type(), unit)
            )
        return '{}_TRUNC({}, {})'.format(kind, trans_arg, valid_unit)