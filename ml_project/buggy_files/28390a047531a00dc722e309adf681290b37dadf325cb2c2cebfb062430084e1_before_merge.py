    def __init__(self, typ: mypy.nodes.TypeInfo, args: List[Type],
                 line: int = -1, column: int = -1, erased: bool = False) -> None:
        assert(typ is None or typ.fullname() not in ["builtins.Any", "typing.Any"])
        self.type = typ
        self.args = args
        self.erased = erased
        super().__init__(line, column)