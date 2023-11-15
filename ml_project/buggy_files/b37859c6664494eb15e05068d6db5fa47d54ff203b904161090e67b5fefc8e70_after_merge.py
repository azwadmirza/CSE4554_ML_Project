    def __init__(self, item: Union[Instance, AnyType, TypeVarType, TupleType, NoneTyp,
                                   CallableType], *, line: int = -1, column: int = -1) -> None:
        """To ensure Type[Union[A, B]] is always represented as Union[Type[A], Type[B]], item of
        type UnionType must be handled through make_normalized static method.
        """
        super().__init__(line, column)
        self.item = item