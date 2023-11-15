    def __init__(self, variable_left, variable_right, result):
        assert is_valid_rvalue(variable_left) or isinstance(variable_left, (Contract, Enum))
        assert isinstance(variable_right, Constant)
        assert isinstance(result, ReferenceVariable)
        super().__init__()
        self._variable_left = variable_left
        self._variable_right = variable_right
        self._lvalue = result
        self._gas = None
        self._value = None