    def __init__(self,
                 arg_types: List[Type],
                 arg_kinds: List[int],
                 arg_names: Sequence[Optional[str]],
                 ret_type: Type,
                 fallback: Instance,
                 name: Optional[str] = None,
                 definition: Optional[SymbolNode] = None,
                 variables: Optional[List[TypeVarDef]] = None,
                 line: int = -1,
                 column: int = -1,
                 is_ellipsis_args: bool = False,
                 implicit: bool = False,
                 is_classmethod_class: bool = False,
                 special_sig: Optional[str] = None,
                 from_type_type: bool = False,
                 bound_args: Optional[List[Optional[Type]]] = None,
                 ) -> None:
        assert len(arg_types) == len(arg_kinds) == len(arg_names)
        if variables is None:
            variables = []
        assert len(arg_types) == len(arg_kinds)
        assert not any(tp is None for tp in arg_types), "No annotation must be Any, not None"
        self.arg_types = arg_types
        self.arg_kinds = arg_kinds
        self.arg_names = list(arg_names)
        self.min_args = arg_kinds.count(ARG_POS)
        self.is_var_arg = ARG_STAR in arg_kinds
        self.is_kw_arg = ARG_STAR2 in arg_kinds
        self.ret_type = ret_type
        self.fallback = fallback
        assert not name or '<bound method' not in name
        self.name = name
        self.definition = definition
        self.variables = variables
        self.is_ellipsis_args = is_ellipsis_args
        self.implicit = implicit
        self.is_classmethod_class = is_classmethod_class
        self.special_sig = special_sig
        self.from_type_type = from_type_type
        self.bound_args = bound_args or []
        super().__init__(line, column)