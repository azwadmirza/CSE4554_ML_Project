    def get_fetch_op_cls(self, obj):
        output_types = get_output_types(obj, unknown_as=OutputType.object)
        fetch_cls, fetch_shuffle_cls = get_fetch_class(output_types[0])
        if isinstance(self, ShuffleProxy):
            cls = fetch_shuffle_cls
        else:
            cls = fetch_cls

        def _inner(**kw):
            return cls(output_types=output_types, **kw)

        return _inner