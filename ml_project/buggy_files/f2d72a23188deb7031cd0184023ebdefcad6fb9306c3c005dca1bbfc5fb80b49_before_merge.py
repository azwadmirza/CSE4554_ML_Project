    def __init__(self, values, dtype: ArrowDtype = None, copy=False):
        if isinstance(values, (pd.Index, pd.Series)):
            # for pandas Index and Series,
            # convert to PandasArray
            values = values.array

        if isinstance(values, type(self)):
            arrow_array = values._arrow_array
        elif isinstance(values, ExtensionArray):
            # if come from pandas object like index,
            # convert to pandas StringArray first,
            # validation will be done in construct
            arrow_array = pa.chunked_array([pa.array(values, from_pandas=True)])
        elif isinstance(values, pa.ChunkedArray):
            arrow_array = values
        elif isinstance(values, pa.Array):
            arrow_array = pa.chunked_array([values])
        else:
            arrow_array = pa.chunked_array([pa.array(values, type=dtype.arrow_type)])

        if copy:
            arrow_array = copy_obj(arrow_array)

        self._arrow_array = arrow_array
        self._dtype = dtype

        # for test purpose
        self._force_use_pandas = False