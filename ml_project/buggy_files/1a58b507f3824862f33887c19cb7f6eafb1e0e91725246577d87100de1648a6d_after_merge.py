    def imports(self, path, dest=None, info_folder=None, cwd=None):
        """
        :param path: Path to the conanfile
        :param dest: Dir to put the imported files. (Abs path or relative to cwd)
        :param info_folder: Dir where the conaninfo.txt and conanbuildinfo.txt files are
        :param cwd: Current working directory
        :return: None
        """
        cwd = cwd or get_cwd()
        info_folder = _make_abs_path(info_folder, cwd)
        dest = _make_abs_path(dest, cwd)

        remotes = self._cache.registry.load_remotes()
        self.python_requires.enable_remotes(remotes=remotes)
        mkdir(dest)
        conanfile_abs_path = _get_conanfile_path(path, cwd, py=None)
        conanfile = self._graph_manager.load_consumer_conanfile(conanfile_abs_path, info_folder,
                                                                deps_info_required=True)
        run_imports(conanfile, dest)