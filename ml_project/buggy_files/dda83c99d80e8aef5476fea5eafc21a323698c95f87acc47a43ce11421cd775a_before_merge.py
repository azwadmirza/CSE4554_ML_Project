    def __call__(self, wrap):
        setattr(wrap, IS_STRAWBERRY_FIELD, True)

        self.field_description = self.field_description or wrap.__doc__

        return LazyFieldWrapper(
            wrap,
            is_input=self.is_input,
            is_subscription=self.is_subscription,
            resolver=self.field_resolver,
            name=self.field_name,
            description=self.field_description,
            permission_classes=self.field_permission_classes,
        )