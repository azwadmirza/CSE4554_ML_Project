    def _merge_dirs(self, ancestor_info, our_info, their_info):
        from operator import itemgetter

        from dictdiffer import patch

        ancestor = self._to_dict(ancestor_info)
        our = self._to_dict(our_info)
        their = self._to_dict(their_info)

        our_diff = self._diff(ancestor, our)
        if not our_diff:
            return self._from_dict(their)

        their_diff = self._diff(ancestor, their)
        if not their_diff:
            return self._from_dict(our)

        # make sure there are no conflicting files
        self._diff(our, their, allow_removed=True)

        merged = patch(our_diff + their_diff, ancestor, in_place=True)

        # Sorting the list by path to ensure reproducibility
        return sorted(
            self._from_dict(merged), key=itemgetter(self.tree.PARAM_RELPATH)
        )