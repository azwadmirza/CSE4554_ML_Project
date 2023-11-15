    def _get_branch_containing(self, rev):
        from git.exc import GitCommandError

        try:
            names = self.scm.repo.git.branch(contains=rev).strip().splitlines()

            if (
                names
                and self.scm.repo.head.is_detached
                and names[0].startswith("* (HEAD detached")
            ):
                # Ignore detached head entry if it exists
                del names[0]

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