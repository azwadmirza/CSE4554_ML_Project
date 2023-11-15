    def _maybe_coerce_merge_keys(self):
        # we have valid mergees but we may have to further
        # coerce these if they are originally incompatible types
        #
        # for example if these are categorical, but are not dtype_equal
        # or if we have object and integer dtypes

        for lk, rk, name in zip(self.left_join_keys,
                                self.right_join_keys,
                                self.join_names):
            if (len(lk) and not len(rk)) or (not len(lk) and len(rk)):
                continue

            lk_is_cat = is_categorical_dtype(lk)
            rk_is_cat = is_categorical_dtype(rk)

            # if either left or right is a categorical
            # then the must match exactly in categories & ordered
            if lk_is_cat and rk_is_cat:
                if lk.is_dtype_equal(rk):
                    continue

            elif lk_is_cat or rk_is_cat:
                pass

            elif is_dtype_equal(lk.dtype, rk.dtype):
                continue

            # if we are numeric, then allow differing
            # kinds to proceed, eg. int64 and int8
            # further if we are object, but we infer to
            # the same, then proceed
            if is_numeric_dtype(lk) and is_numeric_dtype(rk):
                if lk.dtype.kind == rk.dtype.kind:
                    continue

                # let's infer and see if we are ok
                if lib.infer_dtype(lk) == lib.infer_dtype(rk):
                    continue

            # Houston, we have a problem!
            # let's coerce to object if the dtypes aren't
            # categorical, otherwise coerce to the category
            # dtype. If we coerced categories to object,
            # then we would lose type information on some
            # columns, and end up trying to merge
            # incompatible dtypes. See GH 16900.
            if name in self.left.columns:
                typ = lk.categories.dtype if lk_is_cat else object
                self.left = self.left.assign(
                    **{name: self.left[name].astype(typ)})
            if name in self.right.columns:
                typ = rk.categories.dtype if rk_is_cat else object
                self.right = self.right.assign(
                    **{name: self.right[name].astype(typ)})