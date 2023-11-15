    def where(self, cond, other=None):
        other = _ensure_datetimelike_to_i8(other, to_utc=True)
        values = _ensure_datetimelike_to_i8(self, to_utc=True)
        result = np.where(cond, values, other).astype('i8')

        result = self._ensure_localized(result, from_utc=True)
        return self._shallow_copy(result,
                                  **self._get_attributes_dict())