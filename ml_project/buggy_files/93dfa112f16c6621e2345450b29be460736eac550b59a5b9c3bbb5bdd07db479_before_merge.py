    def check_ignore(self, target):
        full_target = os.path.abspath(target)
        if not self._outside_repo(full_target):
            dirname, basename = os.path.split(os.path.normpath(full_target))
            pattern = self._get_trie_pattern(dirname)
            if pattern:
                matches = pattern.match_details(
                    dirname, basename, os.path.isdir(full_target)
                )

                if matches:
                    return CheckIgnoreResult(target, True, matches)
        return _no_match(target)