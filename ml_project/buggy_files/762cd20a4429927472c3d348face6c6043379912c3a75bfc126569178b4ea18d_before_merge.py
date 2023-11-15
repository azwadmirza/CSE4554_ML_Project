    def __init__(
        self,
        *,
        is_input=False,
        is_subscription=False,
        resolver=None,
        name=None,
        description=None,
        metadata=None,
        permission_classes=None
    ):
        self.field_name = name
        self.field_description = description
        self.field_resolver = resolver
        self.is_subscription = is_subscription
        self.is_input = is_input
        self.field_permission_classes = permission_classes

        super().__init__(
            # TODO:
            default=dataclasses.MISSING,
            default_factory=dataclasses.MISSING,
            init=resolver is None,
            repr=True,
            hash=None,
            # TODO: this needs to be False when init is False
            # we could turn it to True when and if we have a default
            # probably can't be True when passing a resolver
            compare=is_input,
            metadata=metadata,
        )