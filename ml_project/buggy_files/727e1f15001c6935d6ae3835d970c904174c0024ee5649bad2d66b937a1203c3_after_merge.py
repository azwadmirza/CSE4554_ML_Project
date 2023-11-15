    def _execute_combine(cls, df, op):
        if isinstance(op.func, (six.string_types, dict)):
            return df.groupby(level=0, as_index=op.as_index, sort=op.sort).agg(op.func)
        else:
            raise NotImplementedError