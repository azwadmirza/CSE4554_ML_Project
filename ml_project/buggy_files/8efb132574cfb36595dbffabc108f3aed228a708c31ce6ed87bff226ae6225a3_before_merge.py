    def dimension_values(self, dimension, expanded=True, flat=True):
        index = self.get_dimension_index(dimension)
        if index == 0:
            return np.array([self.data])
        elif index == 1:
            return np.array([])
        else:
            return super(VLine, self).dimension_values(dimension)