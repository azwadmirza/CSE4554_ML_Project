    def verify_executables(self):
        """Raise an error if any of the compiler executables is not valid.

        This method confirms that for all of the compilers (cc, cxx, f77, fc)
        that have paths, those paths exist and are executable by the current
        user.
        Raises a CompilerAccessError if any of the non-null paths for the
        compiler are not accessible.
        """
        missing = [cmp for cmp in (self.cc, self.cxx, self.f77, self.fc)
                   if cmp and not (os.path.isfile(cmp) and
                                   os.access(cmp, os.X_OK))]
        if missing:
            raise CompilerAccessError(self, missing)