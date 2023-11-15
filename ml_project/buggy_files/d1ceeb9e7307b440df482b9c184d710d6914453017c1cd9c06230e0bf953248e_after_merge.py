    def verify_executables(self):
        """Raise an error if any of the compiler executables is not valid.

        This method confirms that for all of the compilers (cc, cxx, f77, fc)
        that have paths, those paths exist and are executable by the current
        user.
        Raises a CompilerAccessError if any of the non-null paths for the
        compiler are not accessible.
        """
        def accessible_exe(exe):
            # compilers may contain executable names (on Cray or user edited)
            if not os.path.isabs(exe):
                exe = spack.util.executable.which_string(exe)
                if not exe:
                    return False
            return os.path.isfile(exe) and os.access(exe, os.X_OK)

        # setup environment before verifying in case we have executable names
        # instead of absolute paths
        with self._compiler_environment():
            missing = [cmp for cmp in (self.cc, self.cxx, self.f77, self.fc)
                       if cmp and not accessible_exe(cmp)]
            if missing:
                raise CompilerAccessError(self, missing)