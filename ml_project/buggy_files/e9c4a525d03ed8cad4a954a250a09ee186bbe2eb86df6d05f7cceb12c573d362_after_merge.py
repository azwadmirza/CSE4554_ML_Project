    def resolve_connection(cls, connection, args, iterable, max_limit=None):
        iterable = maybe_queryset(iterable)

        if isinstance(iterable, QuerySet):
            list_length = iterable.count()
            list_slice_length = (
                min(max_limit, list_length) if max_limit is not None else list_length
            )
        else:
            list_length = len(iterable)
            list_slice_length = (
                min(max_limit, list_length) if max_limit is not None else list_length
            )

        # If after is higher than list_length, connection_from_list_slice
        # would try to do a negative slicing which makes django throw an
        # AssertionError
        after = min(get_offset_with_default(args.get("after"), -1) + 1, list_length)

        if max_limit is not None and "first" not in args:
            args["first"] = max_limit

        connection = connection_from_list_slice(
            iterable[after:],
            args,
            slice_start=after,
            list_length=list_length,
            list_slice_length=list_slice_length,
            connection_type=connection,
            edge_type=connection.Edge,
            pageinfo_type=PageInfo,
        )
        connection.iterable = iterable
        connection.length = list_length
        return connection