    def call(cls, fold_function, **call_kwds):
        def caller(query_compiler, *args, **kwargs):
            axis = call_kwds.get("axis", kwargs.get("axis"))
            return query_compiler.__constructor__(
                query_compiler._modin_frame._fold(
                    cls.validate_axis(axis),
                    lambda x: fold_function(x, *args, **kwargs),
                )
            )

        return caller