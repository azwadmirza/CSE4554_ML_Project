    def _init_packages_map(self):
        if self.__packages_map is not None:
            return self.__packages_map
        self.__packages_map = __packages_map = {}
        pkgs_dir = self.pkgs_dir
        if not isdir(pkgs_dir):
            return __packages_map

        def _add_entry(__packages_map, pkgs_dir, package_filename):
            if not package_filename.endswith(CONDA_TARBALL_EXTENSION):
                package_filename += CONDA_TARBALL_EXTENSION

            dist = first(self.urls_data, lambda x: basename(x) == package_filename,
                         apply=Dist)
            if not dist:
                dist = Dist.from_string(package_filename, channel_override=UNKNOWN_CHANNEL)
            pc_entry = PackageCacheEntry.make_legacy(pkgs_dir, dist)
            __packages_map[pc_entry.dist] = pc_entry

        def dedupe_pkgs_dir_contents(pkgs_dir_contents):
            # if both 'six-1.10.0-py35_0/' and 'six-1.10.0-py35_0.tar.bz2' are in pkgs_dir,
            #   only 'six-1.10.0-py35_0.tar.bz2' will be in the return contents
            contents = []

            def _process(x, y):
                if x + CONDA_TARBALL_EXTENSION != y:
                    contents.append(x)
                return y

            last = reduce(_process, sorted(pkgs_dir_contents))
            _process(last, contents and contents[-1] or '')
            return contents

        pkgs_dir_contents = dedupe_pkgs_dir_contents(listdir(pkgs_dir))

        for base_name in pkgs_dir_contents:
            full_path = join(pkgs_dir, base_name)
            if islink(full_path):
                continue
            elif ((isdir(full_path) and isfile(join(full_path, 'info', 'index.json')))
                  or isfile(full_path) and full_path.endswith(CONDA_TARBALL_EXTENSION)):
                _add_entry(__packages_map, pkgs_dir, base_name)

        return __packages_map