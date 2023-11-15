    def __init__(
            self,
            name: str,
            is_in_init: bool,
            is_init_var: bool,
            has_default: bool,
            line: int,
            column: int,
    ) -> None:
        self.name = name
        self.is_in_init = is_in_init
        self.is_init_var = is_init_var
        self.has_default = has_default
        self.line = line
        self.column = column