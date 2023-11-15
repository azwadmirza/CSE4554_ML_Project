def field(
    f=None,
    *,
    name: Optional[str] = None,
    provides: Optional[List[str]] = None,
    requires: Optional[List[str]] = None,
    external: bool = False,
    is_subscription: bool = False,
    description: Optional[str] = None,
    resolver: Optional[Callable] = None,
    permission_classes: Optional[List[Type[BasePermission]]] = None
):
    return base_field(
        f,
        name=name,
        is_subscription=is_subscription,
        description=description,
        resolver=resolver,
        permission_classes=permission_classes,
        federation=FederationFieldParams(
            provides=provides or [], requires=requires or [], external=external
        ),
    )