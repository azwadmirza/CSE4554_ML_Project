    def create(self):
        """
        Creates the stage directory

        If self.tmp_root evaluates to False, the stage directory is
        created directly under spack.stage_path, otherwise this will
        attempt to create a stage in a temporary directory and link it
        into spack.stage_path.

        Spack will use the first writable location in spack.tmp_dirs
        to create a stage. If there is no valid location in tmp_dirs,
        fall back to making the stage inside spack.stage_path.
        """
        # Create the top-level stage directory
        mkdirp(spack.stage_path)
        remove_dead_links(spack.stage_path)
        # If a tmp_root exists then create a directory there and then link it
        # in the stage area, otherwise create the stage directory in self.path
        if self._need_to_create_path():
            if self.tmp_root:
                tmp_dir = tempfile.mkdtemp('', STAGE_PREFIX, self.tmp_root)
                os.symlink(tmp_dir, self.path)
            else:
                mkdirp(self.path)
        # Make sure we can actually do something with the stage we made.
        ensure_access(self.path)