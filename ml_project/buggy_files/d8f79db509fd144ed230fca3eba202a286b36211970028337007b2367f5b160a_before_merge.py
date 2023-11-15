    def _maybe_coerce_merge_keys(self):
        # we have valid mergee's but we may have to further
        # coerce these if they are originally incompatible types
        #
        # for example if these are categorical, but are not dtype_equal
        # or if we have object and integer dtypes

        for lk, rk, name in zip(self.left_join_keys,
                                self.right_join_keys,
                                self.join_names):
            if (len(lk) and not len(rk)) or (not len(lk) and len(rk)):
                continue

            # if either left or right is a categorical
            # then the must match exactly in categories & ordered
            if is_categorical_dtype(lk) and is_categorical_dtype(rk):
                if lk.is_dtype_equal(rk):
                    continue
            elif is_categorical_dtype(lk) or is_categorical_dtype(rk):
                pass

            elif is_dtype_equal(lk.dtype, rk.dtype):
                continue

            # if we are numeric, then allow differing
            # kinds to proceed, eg. int64 and int8
            # further if we are object, but we infer to
            # the same, then proceed
            if (is_numeric_dtype(lk) and is_numeric_dtype(rk)):
                if lk.dtype.kind == rk.dtype.kind:
                    continue

                # let's infer and see if we are ok
                if lib.infer_dtype(lk) == lib.infer_dtype(rk):
                    continue

            # Houston, we have a problem!
            # let's coerce to object
            if name in self.left.columns:
                self.left = self.left.assign(
                    **{name: self.left[name].astype(object)})
            if name in self.right.columns:
                self.right = self.right.assign(
                    **{name: self.right[name].astype(object)})