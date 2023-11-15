    def persist_changes(self, verbosity=0, output_func=None, **kwargs):
        """Persist changes to files in the given path.

        This also logs the output using the output_func if present.
        """
        # Run all the fixes for all the files and return a dict
        buffer = {}
        for file in self.files:
            if self.num_violations(**kwargs) > 0:
                buffer[file.path] = file.persist_tree(verbosity=verbosity)
                result = buffer[file.path]
            else:
                buffer[file.path] = True
                result = 'SKIP'

            if output_func:
                output_func(
                    format_filename(
                        filename=file.path,
                        success=result,
                        verbose=verbosity)
                )
        return buffer