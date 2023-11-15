    def nearest_branch(self, branch, default="master"):
        # type: (str, str) -> str
        """
        Find the nearest commit in current branch history that exists
        on a different branch and return that branch name.

        If no such branch is found, return the given default ("master" if not
        specified).

        """
        relatives = self.branch_relatives(branch)
        if not relatives:
            return default

        return relatives[0]