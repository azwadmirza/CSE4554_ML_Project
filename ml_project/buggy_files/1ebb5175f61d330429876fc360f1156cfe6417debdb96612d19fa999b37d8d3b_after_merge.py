    def _checkout_default_branch(self):
        from git.refs.symbolic import SymbolicReference

        # switch to default branch
        git_repo = self.scm.repo
        origin_refs = git_repo.remotes["origin"].refs

        # origin/HEAD will point to tip of the default branch unless we
        # initially cloned a repo that was in a detached-HEAD state.
        #
        # If we are currently detached because we cloned a detached
        # repo, we can't actually tell what branch should be considered
        # default, so we just fall back to the first available reference.
        if "HEAD" in origin_refs:
            ref = origin_refs["HEAD"].reference
        else:
            ref = origin_refs[0]
            if not isinstance(ref, SymbolicReference):
                ref = ref.reference
        branch_name = ref.name.split("/")[-1]

        if branch_name in git_repo.heads:
            branch = git_repo.heads[branch_name]
        else:
            branch = git_repo.create_head(branch_name, ref)
            branch.set_tracking_branch(ref)
        branch.checkout()