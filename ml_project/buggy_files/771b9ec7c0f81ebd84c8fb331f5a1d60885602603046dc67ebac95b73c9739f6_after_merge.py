    def get_hashes(self, ireq):
        """
        Given a pinned InstallRequire, returns a set of hashes that represent
        all of the files for a given requirement. It is not acceptable for an
        editable or unpinned requirement to be passed to this function.
        """
        if not is_pinned_requirement(ireq):
            raise TypeError(
                "Expected pinned requirement, not unpinned or editable, got {}".format(ireq))

        # We need to get all of the candidates that match our current version
        # pin, these will represent all of the files that could possibly
        # satisfy this constraint.
        with self.allow_all_wheels():
            all_candidates = self.find_all_candidates(ireq.name)
            candidates_by_version = lookup_table(all_candidates, key=lambda c: c.version)
            matching_versions = list(
                ireq.specifier.filter((candidate.version for candidate in all_candidates)))
            matching_candidates = candidates_by_version[matching_versions[0]]

        return {
            self._get_file_hash(candidate.location)
            for candidate in matching_candidates
        }