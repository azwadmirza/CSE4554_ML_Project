    def __init__(self, lvalue, function, function_type):
        assert isinstance(function_type, FunctionType)
        assert isinstance(function, Variable)
        assert is_valid_lvalue(lvalue) or lvalue is None
        super(InternalDynamicCall, self).__init__()
        self._function = function
        self._function_type = function_type
        self._lvalue = lvalue