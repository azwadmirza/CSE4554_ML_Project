    def broadcast_apply(cls, axis, apply_func, left, right, other_name="r"):
        def mapper(df, others):
            other = pandas.concat(others, axis=axis ^ 1)
            return apply_func(df, **{other_name: other})

        client = _get_global_client()
        return np.array(
            [
                [
                    PandasOnDaskFramePartition(
                        client.submit(
                            deploy_func,
                            part.future,
                            mapper,
                            part.call_queue,
                            [obj[col_idx].call_queue for obj in right]
                            if axis
                            else [obj.call_queue for obj in right[row_idx]],
                            *(
                                [obj[col_idx].future for obj in right]
                                if axis
                                else [obj.future for obj in right[row_idx]]
                            ),
                            pure=False,
                        )
                    )
                    for col_idx, part in enumerate(left[row_idx])
                ]
                for row_idx in range(len(left))
            ]
        )