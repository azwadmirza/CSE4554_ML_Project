    def persist_changes(self, verbosity=0):
        """Run all the fixes for all the files and return a dict."""
        return self.combine_dicts(*[path.persist_changes(verbosity=verbosity) for path in self.paths])