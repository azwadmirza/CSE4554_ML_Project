    def broadcast_apply(cls, axis, apply_func, left, right):
        client = _get_global_client()
        right_parts = np.squeeze(right)
        if len(right_parts.shape) == 0:
            right_parts = np.array([right_parts.item()])
        assert (
            len(right_parts.shape) == 1
        ), "Invalid broadcast partitions shape {}\n{}".format(
            right_parts.shape, [[i.get() for i in j] for j in right_parts]
        )
        return np.array(
            [
                [
                    PandasOnDaskFramePartition(
                        client.submit(
                            deploy_func,
                            part.future,
                            right_parts[col_idx].future
                            if axis
                            else right_parts[row_idx].future,
                            apply_func,
                            part.call_queue,
                            right_parts[col_idx].call_queue
                            if axis
                            else right_parts[row_idx].call_queue,
                            pure=False,
                        )
                    )
                    for col_idx, part in enumerate(left[row_idx])
                ]
                for row_idx in range(len(left))
            ]
        )