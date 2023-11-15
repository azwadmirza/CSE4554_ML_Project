    def _check_recipe_date(self, ref, remote):
        try:
            remote_recipe_manifest, ref = self._remote_manager.get_recipe_manifest(ref, remote)
        except NotFoundException:
            return  # First time uploading this package

        local_manifest = self._cache.package_layout(ref).recipe_manifest()
        if (remote_recipe_manifest != local_manifest and
                remote_recipe_manifest.time > local_manifest.time):
            self._print_manifest_information(remote_recipe_manifest, local_manifest, ref, remote)
            raise ConanException("Remote recipe is newer than local recipe: "
                                 "\n Remote date: %s\n Local date: %s" %
                                 (remote_recipe_manifest.time, local_manifest.time))

        return remote_recipe_manifest