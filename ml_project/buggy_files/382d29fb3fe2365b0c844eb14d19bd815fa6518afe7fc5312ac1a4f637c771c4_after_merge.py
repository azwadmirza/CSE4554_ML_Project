    def semantic_analysis_pass_three(self) -> None:
        assert self.tree is not None, "Internal error: method must be called on parsed file only"
        patches = []  # type: List[Callable[[], None]]
        with self.wrap_context():
            self.manager.semantic_analyzer_pass3.visit_file(self.tree, self.xpath,
                                                            self.options, patches)
            if self.options.dump_type_stats:
                dump_type_stats(self.tree, self.xpath)
        self.patches = patches + self.patches