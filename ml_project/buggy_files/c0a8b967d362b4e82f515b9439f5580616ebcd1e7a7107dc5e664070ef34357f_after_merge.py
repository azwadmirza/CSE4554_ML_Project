    def _get_kw(obj):
        if isinstance(obj, TENSOR_TYPE + TENSOR_CHUNK_TYPE):
            return {'shape': obj.shape,
                    'dtype': obj.dtype,
                    'order': obj.order}
        else:
            return {'shape': obj.shape,
                    'dtypes': obj.dtypes,
                    'index_value': obj.index_value,
                    'columns_value': obj.columns_value}