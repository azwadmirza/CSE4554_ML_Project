    def _read(self):
        """Re-read Database from the data in the set location.

        This does no locking, with one exception: it will automatically
        migrate an index.yaml to an index.json if possible. This requires
        taking a write lock.

        """
        if os.path.isfile(self._index_path):
            # Read from JSON file if a JSON database exists
            self._read_from_file(self._index_path, format='json')

        elif os.path.isfile(self._old_yaml_index_path):
            if os.access(self._db_dir, os.R_OK | os.W_OK):
                # if we can write, then read AND write a JSON file.
                self._read_from_file(self._old_yaml_index_path, format='yaml')
                with WriteTransaction(self.lock, timeout=_db_lock_timeout):
                    self._write(None, None, None)
            else:
                # Read chck for a YAML file if we can't find JSON.
                self._read_from_file(self._old_yaml_index_path, format='yaml')

        else:
            # The file doesn't exist, try to traverse the directory.
            # reindex() takes its own write lock, so no lock here.
            self.reindex(spack.store.layout)