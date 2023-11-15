    def _check_recipe_date(self, conan_ref):
        try:
            remote_recipe_manifest = self._remote_proxy.get_conan_digest(conan_ref)
        except NotFoundException:
            return  # First upload

        local_manifest = self._paths.load_manifest(conan_ref)

        if (remote_recipe_manifest.file_sums != local_manifest.file_sums and
                remote_recipe_manifest.time > local_manifest.time):
            raise ConanException("Remote recipe is newer than local recipe: "
                                 "\n Remote date: %s\n Local date: %s" %
                                 (remote_recipe_manifest.time, local_manifest.time))