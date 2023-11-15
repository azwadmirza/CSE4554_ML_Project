def _make_frozen(ctx: 'mypy.plugin.ClassDefContext', attributes: List[Attribute]) -> None:
    """Turn all the attributes into properties to simulate frozen classes."""
    # TODO: Handle subclasses of frozen classes.
    for attribute in attributes:
        node = ctx.cls.info.names[attribute.name].node
        assert isinstance(node, Var)
        node.is_initialized_in_class = False
        node.is_property = True