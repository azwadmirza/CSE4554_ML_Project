    def schema(self, by_alias=True):
        s = self.type_.schema(by_alias) if hasattr(self.type_, 'schema') else {}
        s.update(
            type=s.get('type') or display_as_type(self.type_),
            title=self._schema.title or s.get('title') or self.alias.title(),
            required=self.required,
        )

        if not self.required and self.default is not None:
            s['default'] = self.default
        if issubclass(self.type_, Enum):
            choice_names = self._schema.choice_names or {}
            s['choices'] = [
                (v.value, choice_names.get(v.value) or k.title())
                for k, v in self.type_.__members__.items()
            ]
        s.update(self._schema.extra)
        return s