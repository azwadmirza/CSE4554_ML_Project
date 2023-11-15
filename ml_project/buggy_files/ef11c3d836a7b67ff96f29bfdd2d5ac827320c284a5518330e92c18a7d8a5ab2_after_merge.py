    def _setitem_when_not_present(self, index, value=_NotSpecified):
        """Perform the fundamental component item creation and storage.

        Components that want to implement a nonstandard storage mechanism
        should override this method.

        Implementations may assume that the index has already been
        validated and is a legitimate entry in the _data dict.
        """
        #
        # If we are a scalar, then idx will be None (_validate_index ensures
        # this)
        if index is None and not self.is_indexed():
            obj = self._data[index] = self
        else:
            obj = self._data[index] = self._ComponentDataClass(component=self)
        try:
            if value is not _NotSpecified:
                obj.set_value(value)
        except:
            del self._data[index]
            raise
        return obj