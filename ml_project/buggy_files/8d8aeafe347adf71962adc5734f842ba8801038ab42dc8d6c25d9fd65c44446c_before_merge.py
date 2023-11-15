    def _resolve_one_round(self):
        """
        Resolves one level of the current constraints, by finding the best
        match for each package in the repository and adding all requirements
        for those best package versions.  Some of these constraints may be new
        or updated.

        Returns whether new constraints appeared in this round.  If no
        constraints were added or changed, this indicates a stable
        configuration.
        """
        # Sort this list for readability of terminal output
        constraints = sorted(self.constraints, key=_dep_key)
        unsafe_constraints = []
        original_constraints = copy.copy(constraints)
        if not self.allow_unsafe:
            for constraint in original_constraints:
                if constraint.name in UNSAFE_PACKAGES:
                    constraints.remove(constraint)
                    constraint.req.specifier = None
                    unsafe_constraints.append(constraint)

        log.debug('Current constraints:')
        for constraint in constraints:
            log.debug('  {}'.format(constraint))

        log.debug('')
        log.debug('Finding the best candidates:')
        best_matches = {self.get_best_match(ireq) for ireq in constraints}

        # Find the new set of secondary dependencies
        log.debug('')
        log.debug('Finding secondary dependencies:')

        safe_constraints = []
        for best_match in best_matches:
            for dep in self._iter_dependencies(best_match):
                if self.allow_unsafe or dep.name not in UNSAFE_PACKAGES:
                    safe_constraints.append(dep)
        # Grouping constraints to make clean diff between rounds
        theirs = set(self._group_constraints(safe_constraints))

        # NOTE: We need to compare RequirementSummary objects, since
        # InstallRequirement does not define equality
        diff = {RequirementSummary(t) for t in theirs} - {RequirementSummary(t) for t in self.their_constraints}
        removed = ({RequirementSummary(t) for t in self.their_constraints} -
                   {RequirementSummary(t) for t in theirs})
        unsafe = ({RequirementSummary(t) for t in unsafe_constraints} -
                  {RequirementSummary(t) for t in self.unsafe_constraints})

        has_changed = len(diff) > 0 or len(removed) > 0 or len(unsafe) > 0
        if has_changed:
            log.debug('')
            log.debug('New dependencies found in this round:')
            for new_dependency in sorted(diff, key=lambda req: key_from_req(req.req)):
                log.debug('  adding {}'.format(new_dependency))
            log.debug('Removed dependencies in this round:')
            for removed_dependency in sorted(removed, key=lambda req: key_from_req(req.req)):
                log.debug('  removing {}'.format(removed_dependency))
            log.debug('Unsafe dependencies in this round:')
            for unsafe_dependency in sorted(unsafe, key=lambda req: key_from_req(req.req)):
                log.debug('  remembering unsafe {}'.format(unsafe_dependency))

        # Store the last round's results in the their_constraints
        self.their_constraints = theirs
        # Store the last round's unsafe constraints
        self.unsafe_constraints = unsafe_constraints
        return has_changed, best_matches