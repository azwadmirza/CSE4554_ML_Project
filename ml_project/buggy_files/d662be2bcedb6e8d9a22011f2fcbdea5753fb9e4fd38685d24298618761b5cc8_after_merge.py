    def setitem(self, axis, key, value):
        """Set the column defined by `key` to the `value` provided.

        Args:
            key: The column name to set.
            value: The value to set the column to.

        Returns:
             A new QueryCompiler
        """
        if axis == 1 or not isinstance(value, type(self)):
            return super().setitem(axis=axis, key=key, value=value)

        try:
            result = self._setitem(axis, key, value)
        # OmniSci engine does not yet support cases when `value` is not a subframe of `self`.
        except NotImplementedError:
            result = super().setitem(axis=axis, key=key, value=value)
        return result