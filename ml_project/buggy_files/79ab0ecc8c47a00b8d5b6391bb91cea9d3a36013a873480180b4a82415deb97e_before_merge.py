        def make_data_scheme_file(record_path):
            # type: (RecordPath) -> File
            normed_path = os.path.normpath(record_path)
            _, scheme_key, dest_subpath = normed_path.split(os.path.sep, 2)
            scheme_path = scheme_paths[scheme_key]
            dest_path = os.path.join(scheme_path, dest_subpath)
            assert_no_path_traversal(scheme_path, dest_path)
            return ZipBackedFile(record_path, dest_path, zip_file)