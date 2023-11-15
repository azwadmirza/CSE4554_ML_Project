    def get_last_remote_commit(self):
        """Return latest locally known remote commit."""
        return self.repository.get_revision_info(self.repository.last_remote_revision)