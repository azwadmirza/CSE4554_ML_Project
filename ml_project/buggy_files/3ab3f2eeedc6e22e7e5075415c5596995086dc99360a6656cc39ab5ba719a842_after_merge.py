    def __init__(self, obj, groupby_obj=None, keys=None, axis=0, level=None, grouper=None,
                 exclusions=None, selection=None, as_index=True, sort=True,
                 group_keys=True, squeeze=False, observed=False, mutated=False,
                 grouper_cache=None):

        def fill_value(v, key):
            return v if v is not None or groupby_obj is None else getattr(groupby_obj, key)

        self.obj = obj
        self.keys = fill_value(keys, 'keys')
        self.axis = fill_value(axis, 'axis')
        self.level = fill_value(level, 'level')
        self.exclusions = fill_value(exclusions, 'exclusions')
        self.selection = selection
        self.as_index = fill_value(as_index, 'as_index')
        self.sort = fill_value(sort, 'sort')
        self.group_keys = fill_value(group_keys, 'group_keys')
        self.squeeze = fill_value(squeeze, 'squeeze')
        self.observed = fill_value(observed, 'observed')
        self.mutated = fill_value(mutated, 'mutated')

        if groupby_obj is None:
            if obj.ndim == 2:
                self.groupby_obj = DataFrameGroupBy(
                    obj, keys=keys, axis=axis, level=level, grouper=grouper, exclusions=exclusions,
                    as_index=as_index, group_keys=group_keys, squeeze=squeeze, observed=observed,
                    mutated=mutated)
            else:
                self.groupby_obj = SeriesGroupBy(
                    obj, keys=keys, axis=axis, level=level, grouper=grouper, exclusions=exclusions,
                    as_index=as_index, group_keys=group_keys, squeeze=squeeze, observed=observed,
                    mutated=mutated)
        else:
            self.groupby_obj = groupby_obj

        if grouper_cache:
            self.groupby_obj.grouper._cache = grouper_cache
        if selection:
            self.groupby_obj = self.groupby_obj[selection]

        self.is_frame = isinstance(self.groupby_obj, DataFrameGroupBy)