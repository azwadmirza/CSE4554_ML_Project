    def lint_string(
        self,
        in_str: str,
        fname: str = "<string input>",
        fix: bool = False,
        config: Optional[FluffConfig] = None,
    ) -> LintedFile:
        """Lint a string.

        Returns:
            :obj:`LintedFile`: an object representing that linted file.

        """
        # Sort out config, defaulting to the built in config if no override
        config = config or self.config

        # Using the new parser, read the file object.
        parsed = self.parse_string(in_str=in_str, fname=fname, config=config)
        time_dict = parsed.time_dict
        vs = parsed.violations
        tree = parsed.tree

        # Look for comment segments which might indicate lines to ignore.
        ignore_buff = []
        if tree:
            for comment in tree.recursive_crawl("comment"):
                if comment.name == "inline_comment":
                    ignore_entry = self.extract_ignore_from_comment(comment)
                    if isinstance(ignore_entry, SQLParseError):
                        vs.append(ignore_entry)
                    elif ignore_entry:
                        ignore_buff.append(ignore_entry)
            if ignore_buff:
                linter_logger.info("Parsed noqa directives from file: %r", ignore_buff)

        if tree:
            t0 = time.monotonic()
            linter_logger.info("LINTING (%s)", fname)
            # If we're in fix mode, apply those fixes.
            # NB: We don't pass in the linting errors, because the fix function
            # regenerates them on each loop.
            if fix:
                tree, initial_linting_errors = self.fix(tree, config=config)
            else:
                initial_linting_errors = self.lint(tree, config=config)

            # Update the timing dict
            t1 = time.monotonic()
            time_dict["linting"] = t1 - t0

            # We're only going to return the *initial* errors, rather
            # than any generated during the fixing cycle.
            vs += initial_linting_errors

        # We process the ignore config here if appropriate
        if config:
            for violation in vs:
                violation.ignore_if_in(config.get("ignore"))

        linted_file = LintedFile(
            fname,
            vs,
            time_dict,
            tree,
            ignore_mask=ignore_buff,
            templated_file=parsed.templated_file,
        )

        # This is the main command line output from linting.
        if self.formatter:
            self.formatter.dispatch_file_violations(
                fname, linted_file, only_fixable=fix
            )

        # Safety flag for unset dialects
        if config.get("dialect") == "ansi" and linted_file.get_violations(
            fixable=True if fix else None, types=SQLParseError
        ):
            if self.formatter:
                self.formatter.dispatch_dialect_warning()

        return linted_file