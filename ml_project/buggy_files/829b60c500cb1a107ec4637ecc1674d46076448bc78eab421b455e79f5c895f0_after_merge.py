    def __init__(self, context, builder, list_type, list_val):
        self._context = context
        self._builder = builder
        self._ty = list_type
        self._list = make_list_cls(list_type)(context, builder, list_val)
        self._itemsize = get_itemsize(context, list_type)
        self._datamodel = context.data_model_manager[list_type.dtype]