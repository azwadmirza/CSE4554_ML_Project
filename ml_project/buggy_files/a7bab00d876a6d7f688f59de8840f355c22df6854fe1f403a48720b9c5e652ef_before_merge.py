    def _write(self):
        """Write the in-memory database index to its file path.

        Does no locking.

        """
        temp_name = '%s.%s.temp' % (socket.getfqdn(), os.getpid())
        temp_file = join_path(self._db_dir, temp_name)

        # Write a temporary database file them move it into place
        try:
            with open(temp_file, 'w') as f:
                self._write_to_yaml(f)
            os.rename(temp_file, self._index_path)

        except:
            # Clean up temp file if something goes wrong.
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise