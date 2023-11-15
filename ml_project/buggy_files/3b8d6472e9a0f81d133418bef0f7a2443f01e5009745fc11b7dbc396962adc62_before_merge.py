    def _shallow_copy(self, values=None, **kwargs):
        if values is not None:
            if 'name' in kwargs:
                kwargs['names'] = kwargs.pop('name', None)
            # discards freq
            kwargs.pop('freq', None)
            return MultiIndex.from_tuples(values, **kwargs)
        return self.view()