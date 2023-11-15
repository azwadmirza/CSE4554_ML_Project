    def __init__(self, func=None, by=None, as_index=None, sort=None, method=None, stage=None, **kw):
        super(DataFrameGroupByAgg, self).__init__(_func=func, _by=by, _as_index=as_index, _sort=sort, _method=method,
                                                  _stage=stage, _object_type=ObjectType.dataframe, **kw)