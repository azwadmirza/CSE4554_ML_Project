    def persist_changes(self, verbosity=0, output_func=None, **kwargs):
        """Run all the fixes for all the files and return a dict."""
        return self.combine_dicts(
            *[
                path.persist_changes(verbosity=verbosity, output_func=output_func, **kwargs)
                for path in self.paths
            ]
        )