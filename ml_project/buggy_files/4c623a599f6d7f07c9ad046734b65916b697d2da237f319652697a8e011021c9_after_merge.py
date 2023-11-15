    def repo_needs_merge(self):
        """Check for unmerged commits from remote repository."""
        try:
            return self.repository.needs_merge()
        except RepositoryException as error:
            report_error(cause="Could check merge needed")
            self.add_alert("MergeFailure", error=self.error_text(error))
            return False