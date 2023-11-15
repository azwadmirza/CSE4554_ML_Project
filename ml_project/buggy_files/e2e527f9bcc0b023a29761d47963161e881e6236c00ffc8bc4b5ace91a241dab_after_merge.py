def _analyze_class(ctx: 'mypy.plugin.ClassDefContext', auto_attribs: bool) -> List[Attribute]:
    """Analyze the class body of an attr maker, its parents, and return the Attributes found."""
    own_attrs = OrderedDict()  # type: OrderedDict[str, Attribute]
    # Walk the body looking for assignments and decorators.
    for stmt in ctx.cls.defs.body:
        if isinstance(stmt, AssignmentStmt):
            for attr in _attributes_from_assignment(ctx, stmt, auto_attribs):
                # When attrs are defined twice in the same body we want to use the 2nd definition
                # in the 2nd location. So remove it from the OrderedDict.
                # Unless it's auto_attribs in which case we want the 2nd definition in the
                # 1st location.
                if not auto_attribs and attr.name in own_attrs:
                    del own_attrs[attr.name]
                own_attrs[attr.name] = attr
        elif isinstance(stmt, Decorator):
            _cleanup_decorator(stmt, own_attrs)

    for attribute in own_attrs.values():
        # Even though these look like class level assignments we want them to look like
        # instance level assignments.
        if attribute.name in ctx.cls.info.names:
            node = ctx.cls.info.names[attribute.name].node
            assert isinstance(node, Var)
            node.is_initialized_in_class = False

    # Traverse the MRO and collect attributes from the parents.
    taken_attr_names = set(own_attrs)
    super_attrs = []
    for super_info in ctx.cls.info.mro[1:-1]:
        if 'attrs' in super_info.metadata:
            for data in super_info.metadata['attrs']['attributes']:
                # Only add an attribute if it hasn't been defined before.  This
                # allows for overwriting attribute definitions by subclassing.
                if data['name'] not in taken_attr_names:
                    a = Attribute.deserialize(super_info, data)
                    super_attrs.append(a)
                    taken_attr_names.add(a.name)
    attributes = super_attrs + list(own_attrs.values())

    # Check the init args for correct default-ness.  Note: This has to be done after all the
    # attributes for all classes have been read, because subclasses can override parents.
    last_default = False
    for attribute in attributes:
        if attribute.init and not attribute.has_default and last_default:
            ctx.api.fail(
                "Non-default attributes not allowed after default attributes.",
                attribute.context)
        last_default = attribute.has_default

    return attributes