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
            return package_cache_record
        except (IOError, OSError):
            # no info/repodata_record.json exists
            # try reading info/index.json
            try:
                index_json_record = read_index_json(extracted_package_dir)
            except (IOError, OSError):
                # info/index.json doesn't exist either
                if isdir(extracted_package_dir) and not isfile(package_tarball_full_path):
                    # We have a directory that looks like a conda package, but without
                    # (1) info/repodata_record.json or info/index.json, and (2) a conda package
                    # tarball, there's not much we can do.  We'll just ignore it.
                    return None

                try:
                    if self.is_writable:
                        if isdir(extracted_package_dir):
                            # We have a partially unpacked conda package directory. Best thing
                            # to do is remove it and try extracting.
                            rm_rf(extracted_package_dir)
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

            # write the info/repodata_record.json file so we can short-circuit this next time
            if self.is_writable:
                repodata_record = PackageRecord.from_objects(package_cache_record)
                repodata_record_path = join(extracted_package_dir, 'info', 'repodata_record.json')
                write_as_json_to_file(repodata_record_path, repodata_record)

            return package_cache_record