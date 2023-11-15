    def semantic_analysis(self) -> None:
        assert self.tree is not None, "Internal error: method must be called on parsed file only"
        patches = []  # type: List[Callable[[], None]]
        with self.wrap_context():
            self.manager.semantic_analyzer.visit_file(self.tree, self.xpath, self.options, patches)
        self.patches = patches