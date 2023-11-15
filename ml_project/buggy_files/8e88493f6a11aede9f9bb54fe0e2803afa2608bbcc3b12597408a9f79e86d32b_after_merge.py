    def binary_operation(cls, axis, left, func, right):
        """
        Apply a function that requires two BasePandasFrame objects.

        Parameters
        ----------
            axis : int
                The axis to apply the function over (0 - rows, 1 - columns)
            left : NumPy array
                The partitions of left Modin Frame
            func : callable
                The function to apply
            right : NumPy array
                The partitions of right Modin Frame.

        Returns
        -------
        NumPy array
            A new BasePandasFrame object, the type of object that called this.
        """
        if axis:
            left_partitions = cls.row_partitions(left)
            right_partitions = cls.row_partitions(right)
        else:
            left_partitions = cls.column_partitions(left)
            right_partitions = cls.column_partitions(right)
        func = cls.preprocess_func(func)
        result = np.array(
            [
                left_partitions[i].apply(
                    func,
                    num_splits=cls._compute_num_partitions(),
                    other_axis_partition=right_partitions[i],
                )
                for i in range(len(left_partitions))
            ]
        )
        return result if axis else result.T