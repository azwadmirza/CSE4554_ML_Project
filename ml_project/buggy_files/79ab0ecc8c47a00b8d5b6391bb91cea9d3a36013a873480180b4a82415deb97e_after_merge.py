        def make_data_scheme_file(record_path):
            # type: (RecordPath) -> File
            normed_path = os.path.normpath(record_path)
            try:
                _, scheme_key, dest_subpath = normed_path.split(os.path.sep, 2)
            except ValueError:
                message = (
                    "Unexpected file in {}: {!r}. .data directory contents"
                    " should be named like: '<scheme key>/<path>'."
                ).format(wheel_path, record_path)
                raise InstallationError(message)

            try:
                scheme_path = scheme_paths[scheme_key]
            except KeyError:
                valid_scheme_keys = ", ".join(sorted(scheme_paths))
                message = (
                    "Unknown scheme key used in {}: {} (for file {!r}). .data"
                    " directory contents should be in subdirectories named"
                    " with a valid scheme key ({})"
                ).format(
                    wheel_path, scheme_key, record_path, valid_scheme_keys
                )
                raise InstallationError(message)

            dest_path = os.path.join(scheme_path, dest_subpath)
            assert_no_path_traversal(scheme_path, dest_path)
            return ZipBackedFile(record_path, dest_path, zip_file)