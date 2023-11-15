    def __init__(self, modules: Dict[str, MypyFile], errors: Errors) -> None:
        self.modules = modules
        self.errors = errors