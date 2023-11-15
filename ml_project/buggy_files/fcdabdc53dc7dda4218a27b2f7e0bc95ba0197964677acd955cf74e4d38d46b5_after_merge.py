    def file_renamed(self, old_name, new_name):
        """
        Update autosave files after a file is renamed.

        Args:
            old_name (str): name of file before it is renamed
            new_name (str): name of file after it is renamed
        """
        try:
            old_hash = self.file_hashes[old_name]
        except KeyError:
            # This should not happen, but it does: spyder-ide/spyder#12396
            logger.error('KeyError when handling rename %s -> %s',
                         old_name, new_name)
            old_hash = None
        self.remove_autosave_file(old_name)
        if old_hash is not None:
            del self.file_hashes[old_name]
            self.file_hashes[new_name] = old_hash
        index = self.stack.has_filename(new_name)
        self.maybe_autosave(index)