    def mean(self, axis, **kwargs):
        if kwargs.get("level") is not None:
            return self.default_to_pandas(pandas.DataFrame.mean, axis=axis, **kwargs)

        skipna = kwargs.get("skipna", True)

        def map_apply_fn(ser, **kwargs):
            try:
                sum_result = ser.sum(skipna=skipna)
                count_result = ser.count()
            except TypeError:
                return None
            else:
                return (sum_result, count_result)

        def reduce_apply_fn(ser, **kwargs):
            sum_result = ser.apply(lambda x: x[0]).sum(skipna=skipna)
            count_result = ser.apply(lambda x: x[1]).sum(skipna=skipna)
            return sum_result / count_result

        def reduce_fn(df, **kwargs):
            df.dropna(axis=1, inplace=True, how="any")
            return build_applyier(reduce_apply_fn, axis=axis)(df)

        def build_applyier(func, **applyier_kwargs):
            def applyier(df, **kwargs):
                result = df.apply(func, **applyier_kwargs)
                return result.set_axis(df.axes[axis ^ 1], axis=0)

            return applyier

        return MapReduceFunction.register(
            build_applyier(map_apply_fn, axis=axis, result_type="reduce"),
            reduce_fn,
            preserve_index=(kwargs.get("numeric_only") is not None),
        )(self, axis=axis, **kwargs)