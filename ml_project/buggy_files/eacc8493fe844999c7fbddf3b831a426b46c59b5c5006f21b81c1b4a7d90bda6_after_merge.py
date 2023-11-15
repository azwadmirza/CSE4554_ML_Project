    def visit_file(self, file_node: MypyFile, fnam: str, options: Options,
                   patches: List[Callable[[], None]]) -> None:
        self.errors.set_file(fnam, file_node.fullname())
        self.options = options
        self.sem.options = options
        self.patches = patches
        self.is_typeshed_file = self.errors.is_typeshed_file(fnam)
        self.sem.globals = file_node.names
        with experiments.strict_optional_set(options.strict_optional):
            self.accept(file_node)