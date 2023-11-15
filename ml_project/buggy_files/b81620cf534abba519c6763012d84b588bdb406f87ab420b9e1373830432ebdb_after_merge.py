    def __init__(self, t, length):
        assert isinstance(t, Type)
        if length:
            if isinstance(length, int):
                length = Literal(length)
            assert isinstance(length, Expression)
            if not isinstance(length, Literal):
                cf = ConstantFolding(length)
                length = cf.result()
        super(ArrayType, self).__init__()
        self._type = t
        self._length = length