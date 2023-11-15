    def __getattr__(self, item):
        """This method is called only when the attribute does not exits
        usually on access to the direct `Settings` object instead of the
        `LazySettings`.
        All first level attributes are stored as UPPERCASE, so self.FOO
        will always be accessible, however in some cases `self.foo` might
        be acessible. This method routes this access to the underlying `_store`
        which handles casing and recursive access.
        """
        try:
            if (
                item.islower()
                and self._store.get("LOWERCASE_READ_FOR_DYNACONF", empty)
                is False
            ):
                raise KeyError
            value = self._store[item]
        except KeyError:
            raise AttributeError(f"Settings has no attribute '{item}'")
        else:
            return value