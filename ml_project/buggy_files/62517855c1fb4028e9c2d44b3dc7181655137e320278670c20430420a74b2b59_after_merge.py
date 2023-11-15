    def get_last_remote_commit(self):
        """Return latest locally known remote commit."""
        try:
            revision = self.repository.last_remote_revision
        except RepositoryException as error:
            report_error(error, prefix="Could not get remote revision")
            return None
        return self.repository.get_revision_info(revision)