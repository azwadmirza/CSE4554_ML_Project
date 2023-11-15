    def _process_input(x):
        if isinstance(x, (DATAFRAME_TYPE, SERIES_TYPE)) or np.isscalar(x):
            return x
        elif isinstance(x, pd.Series):
            return Series(x)
        elif isinstance(x, pd.DataFrame):
            return DataFrame(x)
        elif isinstance(x, (list, tuple, np.ndarray, TENSOR_TYPE)):
            return astensor(x)
        raise NotImplementedError