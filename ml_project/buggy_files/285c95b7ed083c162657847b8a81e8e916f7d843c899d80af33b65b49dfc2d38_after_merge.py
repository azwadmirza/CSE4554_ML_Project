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
            return np.array([self.data if np.isscalar(self.data) else self.data[index]])
        elif index == 1:
            return [] if np.isscalar(self.data) else np.array([self.data[1]])
        else:
            return super(Annotation, self).dimension_values(dimension)