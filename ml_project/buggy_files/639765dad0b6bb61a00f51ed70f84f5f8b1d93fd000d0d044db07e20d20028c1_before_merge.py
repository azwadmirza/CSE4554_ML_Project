        def func(self, other):
            if isinstance(other, groupby.GroupBy):
                raise TypeError('in-place operations between a Dataset and '
                                'a grouped object are not permitted')
            other_coords = getattr(other, 'coords', None)
            with self.coords._merge_inplace(other_coords):
                # make a defensive copy of variables to modify in-place so we
                # can rollback in case of an exception
                # note: when/if we support automatic alignment, only copy the
                # variables that will actually be included in the result
                dest_vars = dict((k, self._variables[k].copy())
                                 for k in self.data_vars)
                _calculate_binary_op(f, dest_vars, other, dest_vars,
                                     inplace=True)
                self._variables.update(dest_vars)
            return self