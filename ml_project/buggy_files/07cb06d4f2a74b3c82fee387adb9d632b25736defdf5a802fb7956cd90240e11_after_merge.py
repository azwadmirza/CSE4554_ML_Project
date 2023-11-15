def resolve_Type(thing):
    if getattr(thing, "__args__", None) is None:
        return st.just(type)
    args = (thing.__args__[0],)
    if getattr(args[0], "__origin__", None) is typing.Union:
        args = args[0].__args__
    elif hasattr(args[0], "__union_params__"):  # pragma: no cover
        args = args[0].__union_params__
    if isinstance(ForwardRef, type):  # pragma: no cover
        # Duplicate check from from_type here - only paying when needed.
        for a in args:
            if type(a) == ForwardRef:
                raise ResolutionFailed(
                    "thing=%s cannot be resolved.  Upgrading to "
                    "python>=3.6 may fix this problem via improvements "
                    "to the typing module." % (thing,)
                )
    return st.sampled_from(sorted(args, key=type_sorting_key))