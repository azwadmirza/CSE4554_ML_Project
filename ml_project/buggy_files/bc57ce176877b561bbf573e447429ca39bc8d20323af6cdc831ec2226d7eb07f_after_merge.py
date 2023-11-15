    def fix(
        self, tree: BaseSegment, config: Optional[FluffConfig] = None
    ) -> Tuple[BaseSegment, List[SQLLintError]]:
        """Return the fixed tree and violations from lintfix when we're fixing."""
        fixed_tree, violations = self.lint_fix(tree, config, fix=True)
        return fixed_tree, violations