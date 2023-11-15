    def load_conanfile(self, conanfile_path, profile, ref, lock_python_requires=None):
        """ load a conanfile with a full reference, name, version, user and channel are obtained
        from the reference, not evaluated. Main way to load from the cache
        """
        conanfile, _ = self.load_basic_module(conanfile_path, lock_python_requires,
                                              ref.user, ref.channel, str(ref))
        conanfile.name = ref.name
        conanfile.version = ref.version

        if profile.dev_reference and profile.dev_reference == ref:
            conanfile.develop = True
        try:
            self._initialize_conanfile(conanfile, profile)
            return conanfile
        except ConanInvalidConfiguration:
            raise
        except Exception as e:  # re-raise with file name
            raise ConanException("%s: %s" % (conanfile_path, str(e)))