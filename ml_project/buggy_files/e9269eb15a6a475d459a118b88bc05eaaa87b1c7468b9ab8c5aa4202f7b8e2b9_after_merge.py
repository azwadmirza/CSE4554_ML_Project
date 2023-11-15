def from_type(thing):
    """Looks up the appropriate search strategy for the given type.

    ``from_type`` is used internally to fill in missing arguments to
    :func:`~hypothesis.strategies.builds` and can be used interactively
    to explore what strategies are available or to debug type resolution.

    You can use :func:`~hypothesis.strategies.register_type_strategy` to
    handle your custom types, or to globally redefine certain strategies -
    for example excluding NaN from floats, or use timezone-aware instead of
    naive time and datetime strategies.

    The resolution logic may be changed in a future version, but currently
    tries these four options:

    1. If ``thing`` is in the default lookup mapping or user-registered lookup,
       return the corresponding strategy.  The default lookup covers all types
       with Hypothesis strategies, including extras where possible.
    2. If ``thing`` is from the :mod:`python:typing` module, return the
       corresponding strategy (special logic).
    3. If ``thing`` has one or more subtypes in the merged lookup, return
       the union of the strategies for those types that are not subtypes of
       other elements in the lookup.
    4. Finally, if ``thing`` has type annotations for all required arguments,
       it is resolved via :func:`~hypothesis.strategies.builds`.

    """
    from hypothesis.searchstrategy import types
    if not isinstance(thing, type):
        try:
            # At runtime, `typing.NewType` returns an identity function rather
            # than an actual type, but we can check that for a possible match
            # and then read the magic attribute to unwrap it.
            import typing
            if all([
                hasattr(thing, '__supertype__'), hasattr(typing, 'NewType'),
                isfunction(thing), getattr(thing, '__module__', 0) == 'typing'
            ]):
                return from_type(thing.__supertype__)
            # Under Python 3.6, Unions are not instances of `type` - but we
            # still want to resolve them!
            if getattr(thing, '__origin__', None) is typing.Union:
                args = sorted(thing.__args__, key=types.type_sorting_key)
                return one_of([from_type(t) for t in args])
        except ImportError:  # pragma: no cover
            pass
        raise InvalidArgument('thing=%s must be a type' % (thing,))
    # Now that we know `thing` is a type, the first step is to check for an
    # explicitly registered strategy.  This is the best (and hopefully most
    # common) way to resolve a type to a strategy.  Note that the value in the
    # lookup may be a strategy or a function from type -> strategy; and we
    # convert empty results into an explicit error.
    if thing in types._global_type_lookup:
        strategy = types._global_type_lookup[thing]
        if not isinstance(strategy, SearchStrategy):
            strategy = strategy(thing)
        if strategy.is_empty:
            raise ResolutionFailed(
                'Error: %r resolved to an empty strategy' % (thing,))
        return strategy
    # If there's no explicitly registered strategy, maybe a subtype of thing
    # is registered - if so, we can resolve it to the subclass strategy.
    # We'll start by checking if thing is from from the typing module,
    # because there are several special cases that don't play well with
    # subclass and instance checks.
    try:
        import typing
        if isinstance(thing, typing.TypingMeta):
            return types.from_typing_type(thing)
    except ImportError:  # pragma: no cover
        pass
    # If it's not from the typing module, we get all registered types that are
    # a subclass of `thing` and are not themselves a subtype of any other such
    # type.  For example, `Number -> integers() | floats()`, but bools() is
    # not included because bool is a subclass of int as well as Number.
    strategies = [
        v if isinstance(v, SearchStrategy) else v(thing)
        for k, v in types._global_type_lookup.items()
        if issubclass(k, thing) and
        sum(types.try_issubclass(k, T) for T in types._global_type_lookup) == 1
    ]
    empty = ', '.join(repr(s) for s in strategies if s.is_empty)
    if empty:
        raise ResolutionFailed(
            'Could not resolve %s to a strategy; consider using '
            'register_type_strategy' % empty)
    elif strategies:
        return one_of(strategies)
    # If we don't have a strategy registered for this type or any subtype, we
    # may be able to fall back on type annotations.
    # Types created via typing.NamedTuple use a custom attribute instead -
    # but we can still use builds(), if we work out the right kwargs.
    if issubclass(thing, tuple) and hasattr(thing, '_fields') \
            and hasattr(thing, '_field_types'):
        kwargs = {k: from_type(thing._field_types[k]) for k in thing._fields}
        return builds(thing, **kwargs)
    # If the constructor has an annotation for every required argument,
    # we can (and do) use builds() without supplying additional arguments.
    required = required_args(thing)
    if not required or required.issubset(get_type_hints(thing.__init__)):
        return builds(thing)
    # We have utterly failed, and might as well say so now.
    raise ResolutionFailed('Could not resolve %r to a strategy; consider '
                           'using register_type_strategy' % (thing,))