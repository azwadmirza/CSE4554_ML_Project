    def update_available(self, conan_reference):
        """Returns 0 if the conanfiles are equal, 1 if there is an update and -1 if
        the local is newer than the remote"""
        if not conan_reference:
            return 0
        read_manifest, _ = self._client_cache.conan_manifests(conan_reference)
        if read_manifest:
            try:  # get_conan_digest can fail, not in server
                upstream_manifest = self.get_conan_digest(conan_reference)
                if upstream_manifest.file_sums != read_manifest.file_sums:
                    return 1 if upstream_manifest.time > read_manifest.time else -1
            except ConanException:
                pass

        return 0