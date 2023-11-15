        def func(self, other):
            if isinstance(other, groupby.GroupBy):
                raise TypeError('in-place operations between a Dataset and '
                                'a grouped object are not permitted')
            if hasattr(other, 'indexes'):
                other = other.reindex_like(self, copy=False)
            # we don't want to actually modify arrays in-place
            g = ops.inplace_to_noninplace_op(f)
            ds = self._calculate_binary_op(g, other, inplace=True)
            self._replace_vars_and_dims(ds._variables, ds._coord_names,
                                        ds._attrs, inplace=True)
            return self