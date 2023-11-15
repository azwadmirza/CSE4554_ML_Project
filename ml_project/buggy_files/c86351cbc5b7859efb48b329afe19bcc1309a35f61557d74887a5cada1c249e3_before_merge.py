def union(name: str, types: typing.Tuple[typing.Type], *, description=None):
    """Creates a new named Union type.

    Example usages:

    >>> strawberry.union(
    >>>     "Name",
    >>>     (A, B),
    >>> )

    >>> strawberry.union(
    >>>     "Name",
    >>>     (A, B),
    >>> )
    """

    from .type_converter import get_graphql_type_for_annotation

    def _resolve_type(root, info, _type):
        if not hasattr(root, "graphql_type"):
            raise WrongReturnTypeForUnion(info.field_name, str(type(root)))

        if is_generic(type(root)):
            return _find_type_for_generic_union(root)

        if root.graphql_type not in _type.types:
            raise UnallowedReturnTypeForUnion(
                info.field_name, str(type(root)), _type.types
            )

        return root.graphql_type

    # TODO: union types don't work with scalar types
    # so we want to return a nice error
    # also we want to make sure we have been passed
    # strawberry types
    graphql_type = GraphQLUnionType(
        name,
        [
            get_graphql_type_for_annotation(type, name, force_optional=True)
            for type in types
        ],
        description=description,
    )
    graphql_type.resolve_type = _resolve_type

    # This is currently a temporary solution, this is ok for now
    # But in future we might want to change this so that it works
    # properly with mypy, but there's no way to return a type like NewType does
    # so we return this class instance as it allows us to reuse the rest of
    # our code without doing too many changes

    class X:
        def __init__(self, graphql_type):
            self.graphql_type = graphql_type

        def __call__(self):
            raise ValueError("Cannot use union type directly")

    return X(graphql_type)