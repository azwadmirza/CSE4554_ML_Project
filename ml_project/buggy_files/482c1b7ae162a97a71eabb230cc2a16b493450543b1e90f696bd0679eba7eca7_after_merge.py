    def visit_file(self, file_node: MypyFile, fnam: str, options: Options,
                   patches: List[Tuple[int, Callable[[], None]]]) -> None:
        self.recurse_into_functions = True
        self.errors.set_file(fnam, file_node.fullname())
        self.options = options
        self.sem.options = options
        self.patches = patches
        self.is_typeshed_file = self.errors.is_typeshed_file(fnam)
        self.sem.cur_mod_id = file_node.fullname()
        self.sem.globals = file_node.names
        with experiments.strict_optional_set(options.strict_optional):
            self.accept(file_node)