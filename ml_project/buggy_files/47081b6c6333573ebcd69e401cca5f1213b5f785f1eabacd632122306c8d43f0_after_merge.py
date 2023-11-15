        def func(self, other):
            if isinstance(other, groupby.GroupBy):
                return NotImplemented
            if hasattr(other, 'indexes'):
                self, other = align(self, other, join=join, copy=False)
                empty_indexes = [d for d, s in self.dims.items() if s == 0]
                if empty_indexes:
                    raise ValueError('no overlapping labels for some '
                                     'dimensions: %s' % empty_indexes)
            g = f if not reflexive else lambda x, y: f(y, x)
            ds = self._calculate_binary_op(g, other, drop_na_vars=drop_na_vars)
            return ds