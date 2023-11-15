        def pre_processor(vals: np.ndarray) -> Tuple[np.ndarray, Optional[Type]]:
            if is_object_dtype(vals):
                raise TypeError(
                    "'quantile' cannot be performed against 'object' dtypes!"
                )

            inference = None
            if is_integer_dtype(vals):
                inference = np.int64
            elif is_datetime64_dtype(vals):
                inference = "datetime64[ns]"
                vals = np.asarray(vals).astype(np.float)

            return vals, inference