    def __init__(self,
                 fail_func: Callable[[str, Context], None],
                 options: Options,
                 is_typeshed_stub: bool) -> None:
        self.fail = fail_func
        self.options = options
        self.is_typeshed_stub = is_typeshed_stub