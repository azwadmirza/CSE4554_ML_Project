def partition_by_callable(type: Type) -> Tuple[List[Type], List[Type]]:
    """Takes in a type and partitions that type into callable subtypes and
    uncallable subtypes.

    Thus, given:
    `callables, uncallables = partition_by_callable(type)`

    If we assert `callable(type)` then `type` has type Union[*callables], and
    If we assert `not callable(type)` then `type` has type Union[*uncallables]

    Guaranteed to not return [], []"""
    if isinstance(type, FunctionLike) or isinstance(type, TypeType):
        return [type], []

    if isinstance(type, AnyType):
        return [type], [type]

    if isinstance(type, UnionType):
        callables = []
        uncallables = []
        for subtype in type.relevant_items():
            subcallables, subuncallables = partition_by_callable(subtype)
            callables.extend(subcallables)
            uncallables.extend(subuncallables)
        return callables, uncallables

    if isinstance(type, TypeVarType):
        return partition_by_callable(type.erase_to_union_or_bound())

    if isinstance(type, Instance):
        method = type.type.get_method('__call__')
        if method and method.type:
            callables, uncallables = partition_by_callable(method.type)
            if len(callables) and not len(uncallables):
                # Only consider the type callable if its __call__ method is
                # definitely callable.
                return [type], []
        return [], [type]

    return [], [type]