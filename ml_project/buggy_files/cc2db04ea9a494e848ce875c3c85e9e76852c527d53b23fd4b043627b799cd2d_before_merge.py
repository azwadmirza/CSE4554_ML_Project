    def where(self, cond, other=None):
        other = _ensure_datetimelike_to_i8(other)
        values = _ensure_datetimelike_to_i8(self)
        result = np.where(cond, values, other).astype('i8')

        result = self._ensure_localized(result)
        return self._shallow_copy(result,
                                  **self._get_attributes_dict())