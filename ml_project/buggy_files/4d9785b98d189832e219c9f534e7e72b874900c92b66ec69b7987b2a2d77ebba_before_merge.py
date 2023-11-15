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
    frozen = _get_decorator_bool_argument(ctx, 'frozen', False)
    cmp = _get_decorator_bool_argument(ctx, 'cmp', True)
    auto_attribs = _get_decorator_bool_argument(ctx, 'auto_attribs', auto_attribs_default)

    if ctx.api.options.python_version[0] < 3:
        if auto_attribs:
            ctx.api.fail("auto_attribs is not supported in Python 2", ctx.reason)
            return
        if not info.defn.base_type_exprs:
            # Note: This will not catch subclassing old-style classes.
            ctx.api.fail("attrs only works with new-style classes", info.defn)
            return

    attributes = _analyze_class(ctx, auto_attribs)

    adder = MethodAdder(info, ctx.api.named_type('__builtins__.function'))
    if init:
        _add_init(ctx, attributes, adder)
    if cmp:
        _add_cmp(ctx, adder)
    if frozen:
        _make_frozen(ctx, attributes)