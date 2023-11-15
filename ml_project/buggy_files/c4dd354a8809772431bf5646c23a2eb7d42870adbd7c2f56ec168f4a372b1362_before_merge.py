    def _make_single_record(self, package_filename):
        if not package_filename.endswith(CONDA_TARBALL_EXTENSION):
            package_filename += CONDA_TARBALL_EXTENSION

        package_tarball_full_path = join(self.pkgs_dir, package_filename)
        log.trace("adding to package cache %s", package_tarball_full_path)
        extracted_package_dir = package_tarball_full_path[:-len(CONDA_TARBALL_EXTENSION)]

        # try reading info/repodata_record.json
        try:
            repodata_record = read_repodata_json(extracted_package_dir)
            package_cache_record = PackageCacheRecord.from_objects(
                repodata_record,
                package_tarball_full_path=package_tarball_full_path,
                extracted_package_dir=extracted_package_dir,
            )
        except (IOError, OSError):
            try:
                index_json_record = read_index_json(extracted_package_dir)
            except (IOError, OSError):
                try:
                    if self.is_writable:
                        extract_tarball(package_tarball_full_path, extracted_package_dir)
                        index_json_record = read_index_json(extracted_package_dir)
                    else:
                        index_json_record = read_index_json_from_tarball(package_tarball_full_path)
                except (EOFError, ReadError):
                    # EOFError: Compressed file ended before the end-of-stream marker was reached
                    # tarfile.ReadError: file could not be opened successfully
                    rm_rf(package_tarball_full_path)
                    return None

            if isfile(package_tarball_full_path):
                md5 = compute_md5sum(package_tarball_full_path)
            else:
                md5 = None

            url = first(self._urls_data, lambda x: basename(x) == package_filename)
            package_cache_record = PackageCacheRecord.from_objects(
                index_json_record,
                url=url,
                md5=md5,
                package_tarball_full_path=package_tarball_full_path,
                extracted_package_dir=extracted_package_dir,
            )
        return package_cache_record