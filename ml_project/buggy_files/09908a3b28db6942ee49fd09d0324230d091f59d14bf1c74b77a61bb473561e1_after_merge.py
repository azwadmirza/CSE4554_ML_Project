    def get_package(self, package_reference, dest_folder, remote):
        """
        Read the conans package from remotes
        Will iterate the remotes to find the conans unless remote was specified

        returns (dict relative_filepath:abs_path , remote_name)"""
        zipped_files = self._call_remote(remote, "get_package", package_reference, dest_folder)
        files = unzip_and_get_files(zipped_files, dest_folder, PACKAGE_TGZ_NAME)
        # Issue #214 https://github.com/conan-io/conan/issues/214
        for dirname, _, files in os.walk(dest_folder):
            for fname in files:
                touch(os.path.join(dirname, fname))

        return files