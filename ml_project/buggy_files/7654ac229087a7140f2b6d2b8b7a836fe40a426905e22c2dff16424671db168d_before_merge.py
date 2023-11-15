    def _create_arithmetic_method(cls, op):
        # Note: this handles both arithmetic and comparison methods.
        def method(self, other):
            is_arithmetic = \
                True if op.__name__ in ops.ARITHMETIC_BINOPS else False

            is_other_array = False
            if not is_scalar(other):
                is_other_array = True
                other = np.asarray(other)

            self_is_na = self.isna()
            other_is_na = pd.isna(other)
            mask = self_is_na | other_is_na

            chunks = []
            mask_chunks = []
            start = 0
            for chunk_array in self._arrow_array.chunks:
                chunk_array = np.asarray(chunk_array.to_pandas())
                end = start + len(chunk_array)
                chunk_mask = mask[start: end]
                chunk_valid = ~chunk_mask

                if is_arithmetic:
                    result = np.empty(chunk_array.shape, dtype=object)
                else:
                    result = np.zeros(chunk_array.shape, dtype=bool)

                chunk_other = other
                if is_other_array:
                    chunk_other = other[start: end]
                    chunk_other = chunk_other[chunk_valid]

                # calculate only for both not None
                result[chunk_valid] = op(chunk_array[chunk_valid],
                                         chunk_other)

                if is_arithmetic:
                    chunks.append(pa.array(result, type=pa.string(),
                                           from_pandas=True))
                else:
                    chunks.append(result)
                    mask_chunks.append(chunk_mask)

            if is_arithmetic:
                return ArrowStringArray(pa.chunked_array(chunks))
            else:
                return pd.arrays.BooleanArray(np.concatenate(chunks),
                                              np.concatenate(mask_chunks))

        return set_function_name(method, f"__{op.__name__}__", cls)