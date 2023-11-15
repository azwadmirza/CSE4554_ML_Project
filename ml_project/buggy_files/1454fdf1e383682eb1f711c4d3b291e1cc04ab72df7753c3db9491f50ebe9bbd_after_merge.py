    def __init__(self, modules: Dict[str, MypyFile], errors: Errors,
                 sem: SemanticAnalyzer) -> None:
        self.modules = modules
        self.errors = errors
        self.sem = sem