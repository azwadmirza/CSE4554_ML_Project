    def lint(
        self, tree: BaseSegment, config: Optional[FluffConfig] = None
    ) -> List[SQLLintError]:
        """Return just the violations from lintfix when we're only linting."""
        _, violations = self.lint_fix(tree, config, fix=False)
        return violations