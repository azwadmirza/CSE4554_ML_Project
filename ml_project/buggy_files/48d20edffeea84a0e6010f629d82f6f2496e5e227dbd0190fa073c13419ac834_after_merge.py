    def update(self, other):
        other_vars = getattr(other, 'variables', other)
        coords = merge_coords([self.variables, other_vars],
                              priority_arg=1, indexes=self.indexes,
                              indexes_from_arg=0)
        self._update_coords(coords)