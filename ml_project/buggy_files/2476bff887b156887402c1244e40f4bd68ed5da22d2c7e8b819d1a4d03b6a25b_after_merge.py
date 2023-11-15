    def _setitem_frame(self, key, value):
        # support boolean setting with DataFrame input, e.g.
        # df[df > df2] = 0
        if key.values.size and not com.is_bool_dtype(key.values):
            raise TypeError('Must pass DataFrame with boolean values only')

        self._check_inplace_setting(value)
        self._check_setitem_copy()
        self.where(-key, value, inplace=True)