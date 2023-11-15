        def caller(query_compiler, *args, **kwargs):
            preserve_index = call_kwds.pop("preserve_index", True)
            return query_compiler.__constructor__(
                query_compiler._modin_frame._map_reduce(
                    call_kwds.get("axis")
                    if "axis" in call_kwds
                    else kwargs.get("axis"),
                    lambda x: map_function(x, *args, **kwargs),
                    lambda y: reduce_function(y, *args, **kwargs),
                    preserve_index=preserve_index,
                )
            )