    def __call__(self, implementation):
        if not iscoroutinefunction(implementation.on_field_execution):
            raise NonAwaitableDirective(
                "%s is not awaitable" % repr(implementation)
            )

        SchemaRegistry.register_directive(self._schema_name, self)

        self._implementation = implementation
        return implementation