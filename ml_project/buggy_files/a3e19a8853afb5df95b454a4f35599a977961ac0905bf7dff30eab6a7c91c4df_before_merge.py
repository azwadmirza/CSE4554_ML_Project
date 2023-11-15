    def __init__(self,
                 lookup_func: Callable[[str, Context], SymbolTableNode],
                 lookup_fqn_func: Callable[[str], SymbolTableNode],
                 tvar_scope: TypeVarScope,
                 fail_func: Callable[[str, Context], None],
                 plugin: Plugin,
                 options: Options,
                 is_typeshed_stub: bool, *,
                 aliasing: bool = False,
                 allow_tuple_literal: bool = False,
                 allow_unnormalized: bool = False) -> None:
        self.lookup = lookup_func
        self.lookup_fqn_func = lookup_fqn_func
        self.fail_func = fail_func
        self.tvar_scope = tvar_scope
        self.aliasing = aliasing
        self.allow_tuple_literal = allow_tuple_literal
        # Positive if we are analyzing arguments of another (outer) type
        self.nesting_level = 0
        self.allow_unnormalized = allow_unnormalized
        self.plugin = plugin
        self.options = options
        self.is_typeshed_stub = is_typeshed_stub