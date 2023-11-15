    def call(cls, reduction_function, **call_kwds):
        def caller(query_compiler, *args, **kwargs):
            preserve_index = call_kwds.pop("preserve_index", True)
            axis = call_kwds.get("axis", kwargs.get("axis"))
            return query_compiler.__constructor__(
                query_compiler._modin_frame._fold_reduce(
                    cls.validate_axis(axis),
                    lambda x: reduction_function(x, *args, **kwargs),
                    preserve_index=preserve_index,
                )
            )

        return caller