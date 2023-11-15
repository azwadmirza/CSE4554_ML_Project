    async def bake(
        self,
        custom_default_resolver: Optional[Callable] = None,
        custom_default_type_resolver: Optional[Callable] = None,
    ) -> None:
        """
        Bake the final schema (it should not change after this) used for
        execution.
        :param custom_default_resolver: callable that will replace the builtin
        default_resolver
        :param custom_default_type_resolver: callable that will replace the
        tartiflette `default_type_resolver` (will be called on abstract types
        to deduct the type of a result)
        :type custom_default_resolver: Optional[Callable]
        :type custom_default_type_resolver: Optional[Callable]
        """
        self.default_type_resolver = (
            custom_default_type_resolver or default_type_resolver
        )
        self._inject_introspection_fields()

        self._validate_extensions()  # Validate this before bake
        # TODO maybe a pre_bake/post_bake thing

        try:
            self._bake_extensions()
            await self._bake_types(custom_default_resolver)
        except Exception:  # pylint: disable=broad-except
            # Exceptions should be collected at validation time
            pass

        self._validate()

        # Bake introspection attributes
        self._operation_types = {
            "query": self.type_definitions.get(self.query_operation_name),
            "mutation": self.type_definitions.get(
                self.mutation_operation_name
            ),
            "subscription": self.type_definitions.get(
                self.subscription_operation_name
            ),
        }
        self.queryType = self._operation_types["query"]
        self.mutationType = self._operation_types["mutation"]
        self.subscriptionType = self._operation_types["subscription"]
        self.directives = list(self._directive_definitions.values())

        for type_name, type_definition in self.type_definitions.items():
            if not type_name.startswith("__"):
                self.types.append(type_definition)