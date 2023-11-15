def type_object_type(info: TypeInfo, builtin_type: Callable[[str], Instance]) -> Type:
    """Return the type of a type object.

    For a generic type G with type variables T and S the type is generally of form

      Callable[..., G[T, S]]

    where ... are argument types for the __init__/__new__ method (without the self
    argument). Also, the fallback type will be 'type' instead of 'function'.
    """

    # We take the type from whichever of __init__ and __new__ is first
    # in the MRO, preferring __init__ if there is a tie.
    init_method = info.get('__init__')
    new_method = info.get('__new__')
    if not init_method or not is_valid_constructor(init_method.node):
        # Must be an invalid class definition.
        return AnyType(TypeOfAny.from_error)
    # There *should* always be a __new__ method except the test stubs
    # lack it, so just copy init_method in that situation
    new_method = new_method or init_method
    if not is_valid_constructor(new_method.node):
        # Must be an invalid class definition.
        return AnyType(TypeOfAny.from_error)

    # The two is_valid_constructor() checks ensure this.
    assert isinstance(new_method.node, (FuncBase, Decorator))
    assert isinstance(init_method.node, (FuncBase, Decorator))

    init_index = info.mro.index(init_method.node.info)
    new_index = info.mro.index(new_method.node.info)

    fallback = info.metaclass_type or builtin_type('builtins.type')
    if init_index < new_index:
        method = init_method.node  # type: Union[FuncBase, Decorator]
    elif init_index > new_index:
        method = new_method.node
    else:
        if init_method.node.info.fullname() == 'builtins.object':
            # Both are defined by object.  But if we've got a bogus
            # base class, we can't know for sure, so check for that.
            if info.fallback_to_any:
                # Construct a universal callable as the prototype.
                any_type = AnyType(TypeOfAny.special_form)
                sig = CallableType(arg_types=[any_type, any_type],
                                   arg_kinds=[ARG_STAR, ARG_STAR2],
                                   arg_names=["_args", "_kwds"],
                                   ret_type=any_type,
                                   fallback=builtin_type('builtins.function'))
                return class_callable(sig, info, fallback, None)

        # Otherwise prefer __init__ in a tie. It isn't clear that this
        # is the right thing, but __new__ caused problems with
        # typeshed (#5647).
        method = init_method.node
    # Construct callable type based on signature of __init__. Adjust
    # return type and insert type arguments.
    if isinstance(method, FuncBase):
        t = function_type(method, fallback)
    else:
        assert isinstance(method.type, FunctionLike)  # is_valid_constructor() ensures this
        t = method.type
    return type_object_type_from_function(t, info, method.info, fallback)