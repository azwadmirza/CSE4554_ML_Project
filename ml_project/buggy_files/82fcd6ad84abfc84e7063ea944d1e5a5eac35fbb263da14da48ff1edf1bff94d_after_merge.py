    def broadcast_apply(cls, axis, apply_func, left, right, other_name="r"):
        """Broadcast the right partitions to left and apply a function.

        Note: This will often be overridden by implementations. It materializes the
            entire partitions of the right and applies them to the left through `apply`.

        Parameters
        ----------
            axis: The axis to apply and broadcast over.
            apply_func: The function to apply.
            left: The left partitions.
            right: The right partitions.
            other_name: Name of key-value argument for `apply_func` that
                obtains `right`. (optional, by default it's `"r"`)

        Returns
        -------
            A new `np.array` of partition objects.
        """
        [obj.drain_call_queue() for row in right for obj in row]
        new_right = np.empty(shape=right.shape[axis], dtype=object)

        if axis:
            right = right.T

        for i in range(len(right)):
            new_right[i] = pandas.concat(
                [right[i][j].get() for j in range(len(right[i]))], axis=axis ^ 1
            )
        right = new_right.T if axis else new_right

        new_partitions = np.array(
            [
                [
                    part.add_to_apply_calls(
                        apply_func,
                        **{other_name: right[col_idx] if axis else right[row_idx]},
                    )
                    for col_idx, part in enumerate(left[row_idx])
                ]
                for row_idx in range(len(left))
            ]
        )

        return new_partitions