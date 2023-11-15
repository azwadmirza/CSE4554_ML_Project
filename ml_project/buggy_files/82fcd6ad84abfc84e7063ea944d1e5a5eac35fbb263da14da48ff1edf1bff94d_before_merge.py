    def broadcast_apply(cls, axis, apply_func, left, right):
        """Broadcast the right partitions to left and apply a function.

        Note: This will often be overridden by implementations. It materializes the
            entire partitions of the right and applies them to the left through `apply`.

        Args:
            axis: The axis to apply and broadcast over.
            apply_func: The function to apply.
            left: The left partitions.
            right: The right partitions.

        Returns:
            A new `np.array` of partition objects.
        """
        if right.shape == (1, 1):
            right_parts = right[0]
        else:
            right_parts = np.squeeze(right)

        [obj.drain_call_queue() for obj in right_parts]
        return np.array(
            [
                [
                    part.add_to_apply_calls(
                        apply_func,
                        r=right_parts[col_idx].get()
                        if axis
                        else right_parts[row_idx].get(),
                    )
                    for col_idx, part in enumerate(left[row_idx])
                ]
                for row_idx in range(len(left))
            ]
        )