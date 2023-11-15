    def _validate_setitem_value(self, value):
        value = extract_array(value, extract_numpy=True)

        # require identical categories set
        if isinstance(value, Categorical):
            if not is_dtype_equal(self, value):
                raise ValueError(
                    "Cannot set a Categorical with another, "
                    "without identical categories"
                )
            new_codes = self._validate_listlike(value)
            value = Categorical.from_codes(new_codes, dtype=self.dtype)

        # wrap scalars and hashable-listlikes in list
        rvalue = value if not is_hashable(value) else [value]

        from pandas import Index

        to_add = Index(rvalue).difference(self.categories)

        # no assignments of values not in categories, but it's always ok to set
        # something to np.nan
        if len(to_add) and not isna(to_add).all():
            raise ValueError(
                "Cannot setitem on a Categorical with a new "
                "category, set the categories first"
            )

        return self._unbox_listlike(rvalue)