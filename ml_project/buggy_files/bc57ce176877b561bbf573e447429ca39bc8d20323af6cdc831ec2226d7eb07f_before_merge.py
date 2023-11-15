    def fix(self, parsed: BaseSegment, config: Optional[FluffConfig] = None):
        """Fix a parsed file object."""
        # Set up our config
        config = config or self.config
        # If we're in fix mode, then we need to progressively call and reconstruct
        working = parsed
        # Keep a set of previous versions to catch infinite loops.
        previous_versions = {working.raw}
        # A placeholder for the fixes we had on the previous loop
        last_fixes = None
        # How many loops have we had
        fix_loop_idx = 0
        # How many loops are we allowed
        loop_limit = config.get("runaway_limit")
        # Keep track of the errors from round 1
        linting_errors = []
        initial_linting_errors = []
        # Enter into the main fix loop. Some fixes may introduce other
        # problems and so we loop around this until we reach stability
        # or we reach the limit.
        while fix_loop_idx < loop_limit:
            fix_loop_idx += 1
            changed = False
            # Iterate through each rule.
            for crawler in self.get_ruleset(config=config):
                # fixes should be a dict {} with keys edit, delete, create
                # delete is just a list of segments to delete
                # edit and create are list of tuples. The first element is the
                # "anchor", the segment to look for either to edit or to insert BEFORE.
                # The second is the element to insert or create.
                lerrs, _, fixes, _ = crawler.crawl(
                    working, dialect=config.get("dialect_obj"), fix=True
                )
                linting_errors += lerrs
                # Are there fixes to apply?
                if fixes:
                    linter_logger.info("Applying Fixes: %s", fixes)
                    # Do some sanity checks on the fixes before applying.
                    if last_fixes and fixes == last_fixes:
                        linter_logger.warning(
                            "One fix for %s not applied, it would re-cause the same error.",
                            crawler.code,
                        )
                    else:
                        last_fixes = fixes
                        # Actually apply fixes.
                        new_working, _ = working.apply_fixes(fixes)
                        # Check for infinite loops
                        if new_working.raw not in previous_versions:
                            # We've not seen this version of the file so far. Continue.
                            working = new_working
                            previous_versions.add(working.raw)
                            changed = True
                            continue
                        # Applying these fixes took us back to a state which we've
                        # seen before. Abort.
                        linter_logger.warning(
                            "One fix for %s not applied, it would re-cause the same error.",
                            crawler.code,
                        )
            # Keep track of initial errors for reporting.
            if fix_loop_idx == 1:
                initial_linting_errors = linting_errors.copy()
            # We did not change the file. Either the file is clean (no fixes), or
            # any fixes which are present will take us back to a previous state.
            if not changed:
                linter_logger.info(
                    "Fix loop complete. Stability achieved after %s/%s loops.",
                    fix_loop_idx,
                    loop_limit,
                )
                break
        else:
            linter_logger.warning(
                "Loop limit on fixes reached [%s]. Some fixes may be overdone.",
                loop_limit,
            )
        return working, initial_linting_errors