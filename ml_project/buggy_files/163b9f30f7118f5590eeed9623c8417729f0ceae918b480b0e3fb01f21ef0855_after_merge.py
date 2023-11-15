    def dimension_values(self, dimension, expanded=True, flat=True):
        """Return the values along the requested dimension.

        Args:
            dimension: The dimension to return values for
            expanded (bool, optional): Whether to expand values
            flat (bool, optional): Whether to flatten array

        Returns:
            NumPy array of values along the requested dimension
        """
        index = self.get_dimension_index(dimension)
        if index == 0:
            return np.array([])
        elif index == 1:
            return np.array([self.data])
        else:
            return super(HLine, self).dimension_values(dimension)