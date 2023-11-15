def is_protocol_implementation(left: Instance, right: Instance,
                               proper_subtype: bool = False) -> bool:
    """Check whether 'left' implements the protocol 'right'.

    If 'proper_subtype' is True, then check for a proper subtype.
    Treat recursive protocols by using the 'assuming' structural subtype matrix
    (in sparse representation, i.e. as a list of pairs (subtype, supertype)),
    see also comment in nodes.TypeInfo. When we enter a check for classes
    (A, P), defined as following::

      class P(Protocol):
          def f(self) -> P: ...
      class A:
          def f(self) -> A: ...

    this results in A being a subtype of P without infinite recursion.
    On every false result, we pop the assumption, thus avoiding an infinite recursion
    as well.
    """
    assert right.type.is_protocol
    # We need to record this check to generate protocol fine-grained dependencies.
    TypeState.record_protocol_subtype_check(left.type, right.type)
    assuming = right.type.assuming_proper if proper_subtype else right.type.assuming
    for (l, r) in reversed(assuming):
        if (mypy.sametypes.is_same_type(l, left)
                and mypy.sametypes.is_same_type(r, right)):
            return True
    with pop_on_exit(assuming, left, right):
        for member in right.type.protocol_members:
            # nominal subtyping currently ignores '__init__' and '__new__' signatures
            if member in ('__init__', '__new__'):
                continue
            ignore_names = member != '__call__'  # __call__ can be passed kwargs
            # The third argument below indicates to what self type is bound.
            # We always bind self to the subtype. (Similarly to nominal types).
            supertype = get_proper_type(find_member(member, right, left))
            assert supertype is not None
            subtype = get_proper_type(find_member(member, left, left))
            # Useful for debugging:
            # print(member, 'of', left, 'has type', subtype)
            # print(member, 'of', right, 'has type', supertype)
            if not subtype:
                return False
            if not proper_subtype:
                # Nominal check currently ignores arg names
                # NOTE: If we ever change this, be sure to also change the call to
                # SubtypeVisitor.build_subtype_kind(...) down below.
                is_compat = is_subtype(subtype, supertype, ignore_pos_arg_names=ignore_names)
            else:
                is_compat = is_proper_subtype(subtype, supertype)
            if not is_compat:
                return False
            if isinstance(subtype, NoneType) and isinstance(supertype, CallableType):
                # We want __hash__ = None idiom to work even without --strict-optional
                return False
            subflags = get_member_flags(member, left.type)
            superflags = get_member_flags(member, right.type)
            if IS_SETTABLE in superflags:
                # Check opposite direction for settable attributes.
                if not is_subtype(supertype, subtype):
                    return False
            if (IS_CLASSVAR in subflags) != (IS_CLASSVAR in superflags):
                return False
            if IS_SETTABLE in superflags and IS_SETTABLE not in subflags:
                return False
            # This rule is copied from nominal check in checker.py
            if IS_CLASS_OR_STATIC in superflags and IS_CLASS_OR_STATIC not in subflags:
                return False

    if not proper_subtype:
        # Nominal check currently ignores arg names, but __call__ is special for protocols
        ignore_names = right.type.protocol_members != ['__call__']
        subtype_kind = SubtypeVisitor.build_subtype_kind(ignore_pos_arg_names=ignore_names)
    else:
        subtype_kind = ProperSubtypeVisitor.build_subtype_kind()
    TypeState.record_subtype_cache_entry(subtype_kind, left, right)
    return True