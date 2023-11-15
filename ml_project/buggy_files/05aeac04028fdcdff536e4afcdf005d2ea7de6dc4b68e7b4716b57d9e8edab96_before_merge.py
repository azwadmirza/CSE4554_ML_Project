    def to_pandas(self) -> Union[np.dtype, PandasExtensionDtype]:
        """Get equivalent pandas data type. """
        return self._pandas_type