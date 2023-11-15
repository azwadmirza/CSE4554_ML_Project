    def visit_file(self, file_node: MypyFile, fnam: str, options: Options) -> None:
        self.errors.set_file(fnam, file_node.fullname())
        self.options = options
        self.is_typeshed_file = self.errors.is_typeshed_file(fnam)
        with experiments.strict_optional_set(options.strict_optional):
            self.accept(file_node)