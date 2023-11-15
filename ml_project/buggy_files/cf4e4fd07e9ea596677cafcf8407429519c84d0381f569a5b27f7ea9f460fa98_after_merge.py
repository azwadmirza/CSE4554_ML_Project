def field(
    f=None,
    *,
    name: Optional[str] = None,
    is_subscription: bool = False,
    description: Optional[str] = None,
    resolver: Optional[Callable] = None,
    permission_classes: Optional[List[Type[BasePermission]]] = None,
    federation: Optional[FederationFieldParams] = None
):
    """Annotates a method or property as a GraphQL field.

    This is normally used inside a type declaration:

    >>> @strawberry.type:
    >>> class X:
    >>>     field_abc: str = strawberry.field(description="ABC")

    >>>     @strawberry.field(description="ABC")
    >>>     def field_with_resolver(self, info) -> str:
    >>>         return "abc"

    it can be used both as decorator and as a normal function.
    """

    origin_name = f.__name__ if f else None
    name = name or (to_camel_case(origin_name) if origin_name else None)

    wrap = StrawberryField(
        field_definition=FieldDefinition(
            origin_name=origin_name,
            name=name,
            type=None,  # type: ignore
            origin=f,  # type: ignore
            description=description,
            base_resolver=resolver,
            is_subscription=is_subscription,
            permission_classes=permission_classes or [],
            arguments=(
                get_arguments_from_resolver(resolver, origin_name) if resolver else []
            ),
            federation=federation or FederationFieldParams(),
        )
    )

    if f:
        return wrap(f)

    return wrap