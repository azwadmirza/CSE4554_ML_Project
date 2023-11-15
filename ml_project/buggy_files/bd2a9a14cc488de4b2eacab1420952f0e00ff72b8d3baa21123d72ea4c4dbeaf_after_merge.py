    def schema(self, by_alias=True):
        s = dict(
            title=self._schema.title or self.alias.title(),
            required=self.required,
        )

        if not self.required and self.default is not None:
            s['default'] = self.default
        s.update(self._schema.extra)

        ts = self.type_schema(by_alias)
        s.update(ts if isinstance(ts, dict) else {'type': ts})
        return s