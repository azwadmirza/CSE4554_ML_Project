    def __init__(self, obj, *args, **kwargs):

        parent = kwargs.pop('parent', None)
        groupby = kwargs.pop('groupby', None)
        if parent is None:
            parent = obj

        # initialize our GroupByMixin object with
        # the resampler attributes
        for attr in self._attributes:
            setattr(self, attr, kwargs.get(attr, getattr(parent, attr)))

        super(_GroupByMixin, self).__init__(None)
        self._groupby = groupby
        self._groupby.mutated = True
        self._groupby.grouper.mutated = True
        self.groupby = copy.copy(parent.groupby)