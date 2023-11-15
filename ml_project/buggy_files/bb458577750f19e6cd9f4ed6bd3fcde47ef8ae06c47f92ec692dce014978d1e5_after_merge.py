    def __init__(self, context, builder, iter_type, iter_val):
        self._context = context
        self._builder = builder
        self._ty = iter_type
        self._iter = make_listiter_cls(iter_type)(context, builder, iter_val)
        self._datamodel = context.data_model_manager[iter_type.yield_type]