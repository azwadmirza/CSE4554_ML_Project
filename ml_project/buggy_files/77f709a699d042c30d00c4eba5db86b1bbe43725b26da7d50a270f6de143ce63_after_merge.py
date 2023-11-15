  def _build_namedtuple(self, name, field_names, field_types, node):
    # Build an InterpreterClass representing the namedtuple.
    if field_types:
      # TODO(mdemello): Fix this to support late types.
      field_types_union = abstract.Union(field_types, self.vm)
    else:
      field_types_union = self.vm.convert.none_type

    members = {n: t.instantiate(node)
               for n, t in moves.zip(field_names, field_types)}

    # collections.namedtuple has: __dict__, __slots__ and _fields.
    # typing.NamedTuple adds: _field_types, __annotations__ and _field_defaults.
    # __slots__ and _fields are tuples containing the names of the fields.
    slots = tuple(self.vm.convert.build_string(node, f) for f in field_names)
    members["__slots__"] = abstract.Tuple(slots, self.vm).to_variable(node)
    members["_fields"] = abstract.Tuple(slots, self.vm).to_variable(node)
    # __dict__ and _field_defaults are both collections.OrderedDicts that map
    # field names (strings) to objects of the field types.
    ordered_dict_cls = self.vm.convert.name_to_value("collections.OrderedDict",
                                                     ast=self.collections_ast)

    # In Python 2, keys can be `str` or `unicode`; support both.
    # In Python 3, `str_type` and `unicode_type` are the same.
    field_keys_union = abstract.Union([self.vm.convert.str_type,
                                       self.vm.convert.unicode_type], self.vm)

    # Normally, we would use abstract_utils.K and abstract_utils.V, but
    # collections.pyi doesn't conform to that standard.
    field_dict_cls = abstract.ParameterizedClass(
        ordered_dict_cls,
        {"K": field_keys_union, "V": field_types_union},
        self.vm)
    members["__dict__"] = field_dict_cls.instantiate(node)
    members["_field_defaults"] = field_dict_cls.instantiate(node)
    # _field_types and __annotations__ are both collections.OrderedDicts
    # that map field names (strings) to the types of the fields.
    field_types_cls = abstract.ParameterizedClass(
        ordered_dict_cls,
        {"K": field_keys_union, "V": self.vm.convert.type_type},
        self.vm)
    members["_field_types"] = field_types_cls.instantiate(node)
    members["__annotations__"] = field_types_cls.instantiate(node)

    # __new__
    # We set the bound on this TypeParameter later. This gives __new__ the
    # signature: def __new__(cls: Type[_Tname], ...) -> _Tname, i.e. the same
    # signature that visitor.CreateTypeParametersForSignatures would create.
    # This allows subclasses of the NamedTuple to get the correct type from
    # their constructors.
    cls_type_param = abstract.TypeParameter(
        visitors.CreateTypeParametersForSignatures.PREFIX + name,
        self.vm, bound=None)
    cls_type = abstract.ParameterizedClass(
        self.vm.convert.type_type, {abstract_utils.T: cls_type_param}, self.vm)
    params = [Param(n, t) for n, t in moves.zip(field_names, field_types)]
    members["__new__"] = overlay_utils.make_method(
        self.vm, node,
        name="__new__",
        self_param=Param("cls", cls_type),
        params=params,
        return_type=cls_type_param,
    )

    # __init__
    members["__init__"] = overlay_utils.make_method(
        self.vm, node,
        name="__init__",
        varargs=Param("args"),
        kwargs=Param("kwargs"))

    # _make
    # _make is a classmethod, so it needs to be wrapped by
    # specialibuiltins.ClassMethodInstance.
    # Like __new__, it uses the _Tname TypeVar.
    sized_cls = self.vm.convert.name_to_value("typing.Sized")
    iterable_type = abstract.ParameterizedClass(
        self.vm.convert.name_to_value("typing.Iterable"),
        {abstract_utils.T: field_types_union}, self.vm)
    cls_type = abstract.ParameterizedClass(
        self.vm.convert.type_type,
        {abstract_utils.T: cls_type_param}, self.vm)
    len_type = abstract.CallableClass(
        self.vm.convert.name_to_value("typing.Callable"),
        {0: sized_cls,
         abstract_utils.ARGS: sized_cls,
         abstract_utils.RET: self.vm.convert.int_type},
        self.vm)
    params = [
        Param("iterable", iterable_type),
        Param("new").unsolvable(self.vm, node),
        Param("len", len_type).unsolvable(self.vm, node)]
    make = overlay_utils.make_method(
        self.vm, node,
        name="_make",
        params=params,
        self_param=Param("cls", cls_type),
        return_type=cls_type_param)
    make_args = function.Args(posargs=(make,))
    _, members["_make"] = self.vm.special_builtins["classmethod"].call(
        node, None, make_args)

    # _replace
    # Like __new__, it uses the _Tname TypeVar. We have to annotate the `self`
    # param to make sure the TypeVar is substituted correctly.
    members["_replace"] = overlay_utils.make_method(
        self.vm, node,
        name="_replace",
        self_param=Param("self", cls_type_param),
        return_type=cls_type_param,
        kwargs=Param("kwds", field_types_union))

    # __getnewargs__
    getnewargs_tuple_params = dict(
        tuple(enumerate(field_types)) +
        ((abstract_utils.T, field_types_union),))
    getnewargs_tuple = abstract.TupleClass(self.vm.convert.tuple_type,
                                           getnewargs_tuple_params, self.vm)
    members["__getnewargs__"] = overlay_utils.make_method(
        self.vm, node,
        name="__getnewargs__",
        return_type=getnewargs_tuple)

    # __getstate__
    members["__getstate__"] = overlay_utils.make_method(
        self.vm, node, name="__getstate__")

    # _asdict
    members["_asdict"] = overlay_utils.make_method(
        self.vm, node,
        name="_asdict",
        return_type=field_dict_cls)

    # Finally, make the class.
    cls_dict = abstract.Dict(self.vm)
    cls_dict.update(node, members)
    if name.__class__ is compat.UnicodeType:
      # Unicode values should be ASCII.
      name = compat.native_str(name.encode("ascii"))

    node, cls_var = self.vm.make_class(
        node=node,
        name_var=self.vm.convert.build_string(node, name),
        bases=[self.vm.convert.tuple_type.to_variable(node)],
        class_dict_var=cls_dict.to_variable(node),
        cls_var=None)
    cls = cls_var.data[0]

    # Now that the class has been made, we can complete the TypeParameter used
    # by __new__, _make and _replace.
    cls_type_param.bound = cls

    return node, cls_var