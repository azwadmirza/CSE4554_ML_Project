    def _load_site_packages(self):
        """
        Load non-conda-installed python packages in the site-packages of the prefix.

        Python packages not handled by conda are installed via other means,
        like using pip or using python setup.py develop for local development.

        Packages found that are not handled by conda are converted into a
        prefix record and handled in memory.

        Packages clobbering conda packages (i.e. the conda-meta record) are
        removed from the in memory representation.
        """
        python_pkg_record = self._python_pkg_record

        if not python_pkg_record:
            return {}

        site_packages_dir = get_python_site_packages_short_path(python_pkg_record.version)
        site_packages_path = join(self.prefix_path, win_path_ok(site_packages_dir))

        if not isdir(site_packages_path):
            return {}

        # Get anchor files for corresponding conda (handled) python packages
        prefix_graph = PrefixGraph(self.iter_records())
        python_records = prefix_graph.all_descendants(python_pkg_record)
        conda_python_packages = get_conda_anchor_files_and_records(python_records)

        # Get all anchor files and compare against conda anchor files to find clobbered conda
        # packages and python packages installed via other means (not handled by conda)
        sp_anchor_files = get_site_packages_anchor_files(site_packages_path, site_packages_dir)
        conda_anchor_files = set(conda_python_packages)
        clobbered_conda_anchor_files = conda_anchor_files - sp_anchor_files
        non_conda_anchor_files = sp_anchor_files - conda_anchor_files

        # If there's a mismatch for anchor files between what conda expects for a package
        # based on conda-meta, and for what is actually in site-packages, then we'll delete
        # the in-memory record for the conda package.  In the future, we should consider
        # also deleting the record on disk in the conda-meta/ directory.
        for conda_anchor_file in clobbered_conda_anchor_files:
            prefix_rec = self._prefix_records.pop(conda_python_packages[conda_anchor_file].name)
            try:
                extracted_package_dir = basename(prefix_rec.extracted_package_dir)
            except AttributeError:
                extracted_package_dir = "-".join((
                    prefix_rec.name, prefix_rec.version, prefix_rec.build
                ))
            prefix_rec_json_path = join(
                self.prefix_path, "conda-meta", '%s.json' % extracted_package_dir
            )
            try:
                rm_rf(prefix_rec_json_path)
            except EnvironmentError:
                log.debug("stale information, but couldn't remove: %s", prefix_rec_json_path)
            else:
                log.debug("removed due to stale information: %s", prefix_rec_json_path)

        # Create prefix records for python packages not handled by conda
        new_packages = {}
        for af in non_conda_anchor_files:
            try:
                python_record = read_python_record(self.prefix_path, af, python_pkg_record.version)
            except EnvironmentError:
                continue
            except ValidationError:
                import sys
                exc_type, exc_value, exc_traceback = sys.exc_info()
                import traceback
                tb = traceback.format_exception(exc_type, exc_value, exc_traceback)
                log.warn("Problem reading non-conda package record at %s. Please verify that you "
                         "still need this, and if so, that this is still installed correctly. "
                         "Reinstalling this package may help.", af)
                log.debug("ValidationError: \n%s\n", "\n".join(tb))
                continue
            if not python_record:
                continue
            self.__prefix_records[python_record.name] = python_record
            new_packages[python_record.name] = python_record

        return new_packages