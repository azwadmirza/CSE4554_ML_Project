def conditional_callable_type_map(expr: Expression,
                                  current_type: Optional[Type],
                                  ) -> Tuple[TypeMap, TypeMap]:
    """Takes in an expression and the current type of the expression.

    Returns a 2-tuple: The first element is a map from the expression to
    the restricted type if it were callable. The second element is a
    map from the expression to the type it would hold if it weren't
    callable."""
    if not current_type:
        return {}, {}

    if isinstance(current_type, AnyType):
        return {}, {}

    callables, uncallables = partition_by_callable(current_type)

    if len(callables) and len(uncallables):
        callable_map = {expr: UnionType.make_union(callables)} if len(callables) else None
        uncallable_map = {expr: UnionType.make_union(uncallables)} if len(uncallables) else None
        return callable_map, uncallable_map

    elif len(callables):
        return {}, None

    return None, {}