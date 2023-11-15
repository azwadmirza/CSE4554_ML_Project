    def update(self, other):
        other_vars = getattr(other, 'variables', other)
        coords = align_and_merge_coords([self.variables, other_vars],
                                        priority_arg=1,
                                        indexes=self.indexes)
        self._update_coords(coords)