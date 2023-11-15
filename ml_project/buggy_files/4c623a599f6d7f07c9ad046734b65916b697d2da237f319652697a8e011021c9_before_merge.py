    def repo_needs_merge(self):
        """Check for unmerged commits from remote repository."""
        return self.repository.needs_merge()