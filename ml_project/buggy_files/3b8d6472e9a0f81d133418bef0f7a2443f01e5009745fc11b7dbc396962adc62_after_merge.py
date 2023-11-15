    def _shallow_copy(self, values=None, **kwargs):
        if values is not None:
            names = kwargs.pop('names', kwargs.pop('name', self.names))
            # discards freq
            kwargs.pop('freq', None)
            return MultiIndex.from_tuples(values, names=names, **kwargs)
        return self.view()