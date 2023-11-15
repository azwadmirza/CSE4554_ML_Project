    def __getattr__(self, name):
        """Allow getting keys from self.store using dot notation"""
        if self._wrapped is empty:
            self._setup()
        if name in self._wrapped._deleted:  # noqa
            raise AttributeError(
                f"Attribute {name} was deleted, " "or belongs to different env"
            )

        if name not in RESERVED_ATTRS:
            lowercase_mode = self._kwargs.get(
                "LOWERCASE_READ_FOR_DYNACONF",
                default_settings.LOWERCASE_READ_FOR_DYNACONF,
            )
            if lowercase_mode is True:
                name = name.upper()

        if (
            name.isupper()
            and (
                self._wrapped._fresh
                or name in self._wrapped.FRESH_VARS_FOR_DYNACONF
            )
            and name not in dir(default_settings)
        ):
            return self._wrapped.get_fresh(name)
        value = getattr(self._wrapped, name)
        if name not in RESERVED_ATTRS:
            return recursively_evaluate_lazy_format(value, self)
        return value