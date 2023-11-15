    def predict(self, data):
        """
        Returns a prediction on the data.

        If the data is a koalas DataFrame, the return is a Koalas Series.

        If the data is a pandas Dataframe, the return is the expected output of the underlying
        pyfunc object (typically a pandas Series or a numpy array).
        """
        if isinstance(data, pd.DataFrame):
            return self._model.predict(data)
        if isinstance(data, DataFrame):
            cols = [data._sdf[n] for n in data.columns]
            return_col = self._model_udf(*cols)
            # TODO: the columns should be named according to the mlflow spec
            # However, this is only possible with spark >= 3.0
            # s = F.struct(*data.columns)
            # return_col = self._model_udf(s)
            return Series(data._internal.copy(scol=return_col), anchor=data)