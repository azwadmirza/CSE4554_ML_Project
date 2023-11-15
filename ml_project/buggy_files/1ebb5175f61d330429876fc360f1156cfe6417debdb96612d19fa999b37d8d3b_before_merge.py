    def _checkout_default_branch(self):
        # switch to default branch
        git_repo = self.scm.repo
        origin_refs = git_repo.remotes["origin"].refs
        ref = origin_refs["HEAD"].reference
        branch_name = ref.name.split("/")[-1]
        if branch_name in git_repo.heads:
            branch = git_repo.heads[branch_name]
        else:
            branch = git_repo.create_head(branch_name, ref)
            branch.set_tracking_branch(ref)
        branch.checkout()