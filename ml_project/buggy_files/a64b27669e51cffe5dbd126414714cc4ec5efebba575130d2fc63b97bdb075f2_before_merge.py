def join_instances(t: Instance, s: Instance) -> ProperType:
    """Calculate the join of two instance types.
    """
    if t.type == s.type:
        # Simplest case: join two types with the same base type (but
        # potentially different arguments).
        if is_subtype(t, s) or is_subtype(s, t):
            # Compatible; combine type arguments.
            args = []  # type: List[Type]
            for i in range(len(t.args)):
                args.append(join_types(t.args[i], s.args[i]))
            return Instance(t.type, args)
        else:
            # Incompatible; return trivial result object.
            return object_from_instance(t)
    elif t.type.bases and is_subtype_ignoring_tvars(t, s):
        return join_instances_via_supertype(t, s)
    else:
        # Now t is not a subtype of s, and t != s. Now s could be a subtype
        # of t; alternatively, we need to find a common supertype. This works
        # in of the both cases.
        return join_instances_via_supertype(s, t)