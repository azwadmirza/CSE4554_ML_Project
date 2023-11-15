    def get_package(self, package_ref, short_paths):
        """ obtain a package, either from disk or retrieve from remotes if necessary
        and not necessary to build
        """
        output = ScopedOutput(str(package_ref.conan), self._out)
        package_folder = self._client_cache.package(package_ref, short_paths=short_paths)

        # Check current package status
        if os.path.exists(package_folder):
            if self._check_updates:
                read_manifest = self._client_cache.load_package_manifest(package_ref)
                try:  # get_conan_digest can fail, not in server
                    upstream_manifest = self.get_package_digest(package_ref)
                    if upstream_manifest.file_sums != read_manifest.file_sums:
                        if upstream_manifest.time > read_manifest.time:
                            output.warn("Current package is older than remote upstream one")
                            if self._update:
                                output.warn("Removing it to retrieve or build an updated one")
                                rmdir(package_folder)
                        else:
                            output.warn("Current package is newer than remote upstream one")
                except ConanException:
                    pass

        installed = False
        local_package = os.path.exists(package_folder)
        if local_package:
            output.info('Already installed!')
            installed = True
            log_package_got_from_local_cache(package_ref)
        else:
            installed = self._retrieve_remote_package(package_ref, package_folder,
                                                      output)
        self.handle_package_manifest(package_ref, installed)
        return installed