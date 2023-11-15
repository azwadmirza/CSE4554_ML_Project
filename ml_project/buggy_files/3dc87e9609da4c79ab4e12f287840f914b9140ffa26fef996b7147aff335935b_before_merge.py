    def __eq__(self, other):
        # pylint: disable=comparison-with-callable
        # see https://github.com/PyCQA/pylint/issues/2306
        if other is None:
            return False
        if isinstance(other, str):
            other = self.from_str_alias(other)
        if self.value == "string" and LEGACY_PANDAS:
            return PandasDtype.String.value == other.value
        elif self.value == "string":
            return self.value == other.value
        return self.str_alias == other.str_alias