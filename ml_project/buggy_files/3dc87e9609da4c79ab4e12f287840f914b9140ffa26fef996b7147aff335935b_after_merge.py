    def __eq__(self, other):
        # pylint: disable=comparison-with-callable
        # see https://github.com/PyCQA/pylint/issues/2306
        if other is None:
            return False
        other_dtype = PandasDtype.get_dtype(other)
        if self.value == "string" and LEGACY_PANDAS:
            return PandasDtype.String.value == other_dtype.value
        elif self.value == "string":
            return self.value == other_dtype.value
        return self.str_alias == other_dtype.str_alias