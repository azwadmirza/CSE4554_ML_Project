def attr_class_maker_callback(ctx: 'mypy.plugin.ClassDefContext',
                              auto_attribs_default: bool = False) -> None:
    """Add necessary dunder methods to classes decorated with attr.s.

    attrs is a package that lets you define classes without writing dull boilerplate code.

    At a quick glance, the decorator searches the class body for assignments of `attr.ib`s (or
    annotated variables if auto_attribs=True), then depending on how the decorator is called,
    it will add an __init__ or all the __cmp__ methods.  For frozen=True it will turn the attrs
    into properties.

    See http://www.attrs.org/en/stable/how-does-it-work.html for information on how attrs works.
    """
    info = ctx.cls.info

    init = _get_decorator_bool_argument(ctx, 'init', True)
    frozen = _get_frozen(ctx)
    cmp = _get_decorator_bool_argument(ctx, 'cmp', True)
    auto_attribs = _get_decorator_bool_argument(ctx, 'auto_attribs', auto_attribs_default)
    kw_only = _get_decorator_bool_argument(ctx, 'kw_only', False)

    if ctx.api.options.python_version[0] < 3:
        if auto_attribs:
            ctx.api.fail("auto_attribs is not supported in Python 2", ctx.reason)
            return
        if not info.defn.base_type_exprs:
            # Note: This will not catch subclassing old-style classes.
            ctx.api.fail("attrs only works with new-style classes", info.defn)
            return
        if kw_only:
            ctx.api.fail(KW_ONLY_PYTHON_2_UNSUPPORTED, ctx.reason)
            return

    attributes = _analyze_class(ctx, auto_attribs, kw_only)

    if ctx.api.options.new_semantic_analyzer:
        # Check if attribute types are ready.
        for attr in attributes:
            node = info.get(attr.name)
            if node is None:
                # This name is likely blocked by a star import. We don't need to defer because
                # defer() is already called by mark_incomplete().
                return
            if node.type is None and not ctx.api.final_iteration:
                ctx.api.defer()
                return

    # Save the attributes so that subclasses can reuse them.
    ctx.cls.info.metadata['attrs'] = {
        'attributes': [attr.serialize() for attr in attributes],
        'frozen': frozen,
    }

    adder = MethodAdder(ctx)
    if init:
        _add_init(ctx, attributes, adder)
    if cmp:
        _add_cmp(ctx, adder)
    if frozen:
        _make_frozen(ctx, attributes)