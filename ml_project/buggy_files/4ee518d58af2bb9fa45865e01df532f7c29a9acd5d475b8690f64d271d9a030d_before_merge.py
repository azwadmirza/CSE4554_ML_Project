    def nearest_branch(self, branch, default="master"):
        # type: (str, str) -> str
        """
        Find the nearest commit in current branch history that exists
        on a different branch and return that branch name.

        We filter these branches through a list of known ancestors which have
        an initial branch point with current branch, and pick the first one
        that matches both.

        If no such branch is found, returns the given default ("master" if not
        specified).

        Solution snagged from:
        http://stackoverflow.com/a/17843908/484127
        http://stackoverflow.com/questions/1527234
        """
        try:
            relatives = self.branch_relatives(branch)
        except GitSavvyError:
            return default

        if not relatives:
            util.debug.add_to_log('nearest_branch: No relatives found. '
                                  'Possibly on a root branch!')
            return default

        util.debug.add_to_log('nearest_branch: found {} relatives: {}'.format(
                              len(relatives), relatives))

        return relatives[0]