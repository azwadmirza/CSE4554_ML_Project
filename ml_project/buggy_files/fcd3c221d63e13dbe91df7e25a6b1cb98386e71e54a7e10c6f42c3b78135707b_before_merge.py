    def _get_branch_containing(self, rev):
        from git.exc import GitCommandError

        if self.scm.repo.head.is_detached:
            self._checkout_default_branch()
        try:
            names = self.scm.repo.git.branch(contains=rev).strip().splitlines()
            if not names:
                return None
            if len(names) > 1:
                raise MultipleBranchError(rev)
            name = names[0]
            if name.startswith("*"):
                name = name[1:]
            return name.rsplit("/")[-1].strip()
        except GitCommandError:
            pass
        return None