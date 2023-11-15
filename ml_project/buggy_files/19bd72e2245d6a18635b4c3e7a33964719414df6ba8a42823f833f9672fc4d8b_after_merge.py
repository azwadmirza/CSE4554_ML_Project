    def _allowed_to_proceed(self, verbose):
        """Display which files would be deleted and prompt for confirmation
        """

        def _display(msg, paths):
            if not paths:
                return

            logger.info(msg)
            with indent_log():
                for path in sorted(compact(paths)):
                    logger.info(path)

        if not verbose:
            will_remove, will_skip = compress_for_output_listing(self.paths)
        else:
            # In verbose mode, display all the files that are going to be
            # deleted.
            will_remove = list(self.paths)
            will_skip = set()

        _display('Would remove:', will_remove)
        _display('Would not remove (might be manually added):', will_skip)
        _display('Would not remove (outside of prefix):', self._refuse)
        if verbose:
            _display('Will actually move:', compress_for_rename(self.paths))

        return ask('Proceed (y/n)? ', ('y', 'n')) == 'y'