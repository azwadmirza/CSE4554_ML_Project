    def _execute_combine(cls, df, op):
        if isinstance(op.func, (six.string_types, dict)):
            return df.groupby(op.by, as_index=op.as_index).agg(op.func)
        else:
            raise NotImplementedError