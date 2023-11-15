    def copy(self, **kw):
        # ticket #5276
        constraint_kwargs = {}
        for dialect_name in self.dialect_options:
            dialect_options = self.dialect_options[dialect_name]._non_defaults
            for (
                dialect_option_key,
                dialect_option_value,
            ) in dialect_options.items():
                constraint_kwargs[
                    dialect_name + "_" + dialect_option_key
                ] = dialect_option_value

        c = self.__class__(
            name=self.name,
            deferrable=self.deferrable,
            initially=self.initially,
            *self.columns.keys(),
            **constraint_kwargs
        )
        return self._schema_item_copy(c)