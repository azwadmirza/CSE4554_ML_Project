    def persist_changes(self, verbosity=0):
        """Persist changes to files in the given path."""
        # Run all the fixes for all the files and return a dict
        return {file.path: file.persist_tree(verbosity=verbosity) for file in self.files}