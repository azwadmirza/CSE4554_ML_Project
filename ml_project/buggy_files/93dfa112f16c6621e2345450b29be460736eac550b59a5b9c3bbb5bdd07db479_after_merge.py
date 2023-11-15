    def check_ignore(self, target):
        # NOTE: can only be used in `dvc check-ignore`, see
        # https://github.com/iterative/dvc/issues/5046
        full_target = os.path.abspath(target)
        if not self._outside_repo(full_target):
            dirname, basename = os.path.split(os.path.normpath(full_target))
            pattern = self._get_trie_pattern(dirname)
            if pattern:
                matches = pattern.matches(
                    dirname, basename, os.path.isdir(full_target), True,
                )

                if matches:
                    return CheckIgnoreResult(target, True, matches)
        return _no_match(target)