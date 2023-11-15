    def _valid_value(self, value):
        if isinstance(value, list):
            assert all(self._valid_value(v) for v in value)
        else:
            assert is_valid_rvalue(value) or isinstance(value, (TupleVariable, Function))
        return True