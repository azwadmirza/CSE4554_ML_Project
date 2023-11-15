    def dimension_values(self, dimension, expanded=True, flat=True):
        index = self.get_dimension_index(dimension)
        if index in [0, 1]:
            return np.array([point[index] for point in self.data[0]])
        else:
            return super(Spline, self).dimension_values(dimension)