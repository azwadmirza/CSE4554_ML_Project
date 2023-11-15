    def compare_values(
        cls,
        ours: ObjectCollection[Object_T],
        theirs: ObjectCollection[Object_T],
        *,
        our_schema: s_schema.Schema,
        their_schema: s_schema.Schema,
        context: ComparisonContext,
        compcoef: float,
    ) -> float:
        if ours is not None:
            our_names = tuple(
                context.get_obj_name(our_schema, obj)
                for obj in ours.objects(our_schema)
            )
        else:
            our_names = cls._container()

        if theirs is not None:
            their_names = theirs.names(their_schema)
        else:
            their_names = cls._container()

        if our_names != their_names:
            return compcoef
        else:
            return 1.0