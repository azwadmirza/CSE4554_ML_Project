def from_typing_type(thing):
    # We start with special-case support for Union and Tuple - the latter
    # isn't actually a generic type.  Support for Callable may be added to
    # this section later.
    # We then explicitly error on non-Generic types, which don't carry enough
    # information to sensibly resolve to strategies at runtime.
    # Finally, we run a variation of the subclass lookup in st.from_type
    # among generic types in the lookup.
    import typing
    # Under 3.6 Union is handled directly in st.from_type, as the argument is
    # not an instance of `type`. However, under Python 3.5 Union *is* a type
    # and we have to handle it here, including failing if it has no parameters.
    if hasattr(thing, '__union_params__'):  # pragma: no cover
        args = sorted(thing.__union_params__ or (), key=type_sorting_key)
        if not args:
            raise ResolutionFailed('Cannot resolve Union of no types.')
        return st.one_of([st.from_type(t) for t in args])
    if getattr(thing, '__origin__', None) == tuple or \
            isinstance(thing, getattr(typing, 'TupleMeta', ())):
        elem_types = getattr(thing, '__tuple_params__', None) or ()
        elem_types += getattr(thing, '__args__', None) or ()
        if getattr(thing, '__tuple_use_ellipsis__', False) or \
                len(elem_types) == 2 and elem_types[-1] is Ellipsis:
            return st.lists(st.from_type(elem_types[0])).map(tuple)
        elif len(elem_types) == 1 and elem_types[0] == ():
            return st.tuples()  # Empty tuple; see issue #1583
        return st.tuples(*map(st.from_type, elem_types))
    if isinstance(thing, typing.TypeVar):
        if getattr(thing, '__bound__', None) is not None:
            return st.from_type(thing.__bound__)
        if getattr(thing, '__constraints__', None):
            return st.shared(
                st.sampled_from(thing.__constraints__),
                key='typevar-with-constraint'
            ).flatmap(st.from_type)
        # Constraints may be None or () on various Python versions.
        return st.text()  # An arbitrary type for the typevar
    # Now, confirm that we're dealing with a generic type as we expected
    if not isinstance(thing, typing_root_type):  # pragma: no cover
        raise ResolutionFailed('Cannot resolve %s to a strategy' % (thing,))
    # Parametrised generic types have their __origin__ attribute set to the
    # un-parametrised version, which we need to use in the subclass checks.
    # e.g.:     typing.List[int].__origin__ == typing.List
    mapping = {k: v for k, v in _global_type_lookup.items()
               if isinstance(k, typing_root_type) and try_issubclass(k, thing)}
    if typing.Dict in mapping:
        # The subtype relationships between generic and concrete View types
        # are sometimes inconsistent under Python 3.5, so we pop them out to
        # preserve our invariant that all examples of from_type(T) are
        # instances of type T - and simplify the strategy for abstract types
        # such as Container
        for t in (typing.KeysView, typing.ValuesView, typing.ItemsView):
            mapping.pop(t, None)
    strategies = [v if isinstance(v, st.SearchStrategy) else v(thing)
                  for k, v in mapping.items()
                  if sum(try_issubclass(k, T) for T in mapping) == 1]
    empty = ', '.join(repr(s) for s in strategies if s.is_empty)
    if empty or not strategies:  # pragma: no cover
        raise ResolutionFailed(
            'Could not resolve %s to a strategy; consider using '
            'register_type_strategy' % (empty or thing,))
    return st.one_of(strategies)