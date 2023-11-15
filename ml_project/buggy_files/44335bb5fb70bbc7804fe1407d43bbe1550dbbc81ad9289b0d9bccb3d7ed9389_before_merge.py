    def __init__(self,
                 lookup_func: Callable[[str, Context], Optional[SymbolTableNode]],
                 lookup_fqn_func: Callable[[str], SymbolTableNode],
                 fail_func: Callable[[str, Context], None],
                 note_func: Callable[[str, Context], None],
                 plugin: Plugin,
                 options: Options,
                 is_typeshed_stub: bool,
                 indicator: Dict[str, bool]) -> None:
        self.lookup_func = lookup_func
        self.lookup_fqn_func = lookup_fqn_func
        self.fail = fail_func
        self.note_func = note_func
        self.options = options
        self.plugin = plugin
        self.is_typeshed_stub = is_typeshed_stub
        self.indicator = indicator