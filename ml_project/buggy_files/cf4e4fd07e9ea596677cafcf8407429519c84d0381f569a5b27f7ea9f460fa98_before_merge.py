def field(
    wrap=None,
    *,
    name=None,
    description=None,
    resolver=None,
    is_input=False,
    is_subscription=False,
    permission_classes=None
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

    field = strawberry_field(
        name=name,
        description=description,
        resolver=resolver,
        is_input=is_input,
        is_subscription=is_subscription,
        permission_classes=permission_classes,
    )

    # when calling this with parens we are going to return a strawberry_field
    # instance, so it can be used as both decorator and function.

    if wrap is None:
        return field

    # otherwise we run the decorator directly,
    # when called as @strawberry.field, without parens.

    return field(wrap)