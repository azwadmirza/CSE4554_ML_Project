    def default_to_pandas(self, pandas_op, *args, **kwargs):
        """Default to pandas behavior.

        Parameters
        ----------
        pandas_op : callable
            The operation to apply, must be compatible pandas DataFrame call
        args
            The arguments for the `pandas_op`
        kwargs
            The keyword arguments for the `pandas_op`

        Returns
        -------
        PandasQueryCompiler
            The result of the `pandas_op`, converted back to PandasQueryCompiler

        Note
        ----
        This operation takes a distributed object and converts it directly to pandas.
        """
        ErrorMessage.default_to_pandas(str(pandas_op))
        args = (a.to_pandas() if isinstance(a, type(self)) else a for a in args)
        kwargs = {
            k: v.to_pandas if isinstance(v, type(self)) else v
            for k, v in kwargs.items()
        }

        result = pandas_op(self.to_pandas(), *args, **kwargs)
        if isinstance(result, pandas.Series):
            result = result.to_frame()
        if isinstance(result, pandas.DataFrame):
            return self.from_pandas(result, type(self._modin_frame))
        else:
            return result