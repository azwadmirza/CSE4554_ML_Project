def _transform_attrs(cls, these):
    """
    Transforms all `_CountingAttr`s on a class into `Attribute`s and saves the
    list in `__attrs_attrs__`.

    If *these* is passed, use that and don't look for them on the class.
    """
    super_cls = []
    for c in reversed(cls.__mro__[1:-1]):
        sub_attrs = getattr(c, "__attrs_attrs__", None)
        if sub_attrs is not None:
            super_cls.extend(a for a in sub_attrs if a not in super_cls)
    if these is None:
        ca_list = [(name, attr)
                   for name, attr
                   in cls.__dict__.items()
                   if isinstance(attr, _CountingAttr)]
    else:
        ca_list = [(name, ca)
                   for name, ca
                   in iteritems(these)]

    non_super_attrs = [
        Attribute.from_counting_attr(name=attr_name, ca=ca)
        for attr_name, ca
        in sorted(ca_list, key=lambda e: e[1].counter)
    ]
    attr_names = [a.name for a in super_cls + non_super_attrs]

    AttrsClass = _make_attr_tuple_class(cls.__name__, attr_names)

    cls.__attrs_attrs__ = AttrsClass(super_cls + [
        Attribute.from_counting_attr(name=attr_name, ca=ca)
        for attr_name, ca
        in sorted(ca_list, key=lambda e: e[1].counter)
    ])

    had_default = False
    for a in cls.__attrs_attrs__:
        if these is None and a not in super_cls:
            setattr(cls, a.name, a)
        if had_default is True and a.default is NOTHING and a.init is True:
            raise ValueError(
                "No mandatory attributes allowed after an attribute with a "
                "default value or factory.  Attribute in question: {a!r}"
                .format(a=a)
            )
        elif had_default is False and \
                a.default is not NOTHING and \
                a.init is not False:
            had_default = True