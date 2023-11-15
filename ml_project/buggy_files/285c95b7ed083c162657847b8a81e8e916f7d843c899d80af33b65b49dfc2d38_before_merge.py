    def dimension_values(self, dimension, expanded=True, flat=True):
        index = self.get_dimension_index(dimension)
        if index == 0:
            return np.array([self.data if np.isscalar(self.data) else self.data[index]])
        elif index == 1:
            return [] if np.isscalar(self.data) else np.array([self.data[1]])
        else:
            return super(Annotation, self).dimension_values(dimension)