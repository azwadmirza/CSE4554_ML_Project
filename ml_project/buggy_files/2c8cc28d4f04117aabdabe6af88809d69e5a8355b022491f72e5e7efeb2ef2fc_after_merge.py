    def get_paths(self):
        """
        Read the list of installed paths from record or source file.

        Example
        -------
        [(u'skdata/__init__.py', u'sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU', 0),
         (u'skdata/diabetes.py', None, None),
         ...
        ]
        """
        manifest_full_path = self.manifest_full_path
        if manifest_full_path:
            python_version = self.python_version
            sp_dir = get_python_site_packages_short_path(python_version) + "/"
            prepend_metadata_dirname = basename(manifest_full_path) == "installed-files.txt"
            if prepend_metadata_dirname:
                path_prepender = basename(dirname(manifest_full_path)) + "/"
            else:
                path_prepender = ""

            def process_csv_row(reader):
                seen = []
                records = []
                for row in reader:
                    cleaned_path = posix_normpath("%s%s%s" % (sp_dir, path_prepender, row[0]))
                    if len(row) == 3:
                        checksum, size = row[1:]
                        if checksum:
                            assert checksum.startswith('sha256='), (self._metadata_dir_full_path,
                                                                    cleaned_path, checksum)
                            checksum = checksum[7:]
                        else:
                            checksum = None
                        size = int(size) if size else None
                    else:
                        checksum = size = None
                    if cleaned_path not in seen and row[0]:
                        seen.append(cleaned_path)
                        records.append((cleaned_path, checksum, size))
                    else:
                        continue
                return tuple(records)

            csv_delimiter = ','
            if PY2:
                csv_delimiter = csv_delimiter.encode('utf-8')
            with open(manifest_full_path) as csvfile:
                record_reader = csv_reader(csvfile, delimiter=csv_delimiter)
                # format of each record is (path, checksum, size)
                records = process_csv_row(record_reader)
            files_set = set(record[0] for record in records)

            _pyc_path, _py_file_re = pyc_path, PY_FILE_RE
            py_ver_mm = get_major_minor_version(python_version, with_dot=False)
            missing_pyc_files = (ff for ff in (
                _pyc_path(f, py_ver_mm) for f in files_set if _py_file_re.match(f)
            ) if ff not in files_set)
            records = sorted(concatv(records, ((pf, None, None) for pf in missing_pyc_files)))
            return records

        return []