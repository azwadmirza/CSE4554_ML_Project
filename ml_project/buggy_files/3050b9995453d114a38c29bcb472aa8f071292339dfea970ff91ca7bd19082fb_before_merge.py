    def editable_add(self, path, reference, layout, cwd):
        # Retrieve conanfile.py from target_path
        target_path = _get_conanfile_path(path=path, cwd=cwd, py=True)

        # Check the conanfile is there, and name/version matches
        ref = ConanFileReference.loads(reference, validate=True)
        target_conanfile = self._graph_manager._loader.load_class(target_path)
        if (target_conanfile.name and target_conanfile.name != ref.name) or \
                (target_conanfile.version and target_conanfile.version != ref.version):
            raise ConanException("Name and version from reference ({}) and target "
                                 "conanfile.py ({}/{}) must match".
                                 format(ref, target_conanfile.name, target_conanfile.version))

        layout_abs_path = get_editable_abs_path(layout, cwd, self._cache.conan_folder)
        if layout_abs_path:
            self._user_io.out.success("Using layout file: %s" % layout_abs_path)
        self._cache.editable_packages.add(ref, os.path.dirname(target_path), layout_abs_path)