    def __init__(self, by=None, as_index=None, sort=None, object_type=ObjectType.groupby, **kw):
        super(DataFrameGroupByOperand, self).__init__(_by=by, _as_index=as_index, _sort=sort,
                                                      _object_type=object_type, **kw)