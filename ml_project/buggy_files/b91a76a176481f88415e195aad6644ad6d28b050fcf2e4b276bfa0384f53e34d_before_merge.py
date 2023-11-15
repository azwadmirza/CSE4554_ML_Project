    def lint(
        self, parsed: BaseSegment, config: Optional[FluffConfig] = None
    ) -> List[SQLLintError]:
        """Lint a parsed file object."""
        config = config or self.config
        linting_errors = []
        for crawler in self.get_ruleset(config=config):
            lerrs, _, _, _ = crawler.crawl(parsed, dialect=config.get("dialect_obj"))
            linting_errors += lerrs

        # Filter out any linting errors in templated sections if relevant.
        if config.get("ignore_templated_areas", default=True):
            linting_errors = list(
                filter(
                    lambda e: getattr(e.segment.pos_marker, "is_literal", True),
                    linting_errors,
                )
            )

        return linting_errors