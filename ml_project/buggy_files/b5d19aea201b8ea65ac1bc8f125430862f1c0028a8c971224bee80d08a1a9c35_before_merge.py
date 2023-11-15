    def define(self, remotes):
        # For definition from conan config install
        for ref in self._cache.all_refs():
            with self._cache.package_layout(ref).update_metadata() as metadata:
                if metadata.recipe.remote not in remotes:
                    metadata.recipe.remote = None
                for pkg_metadata in metadata.packages.values():
                    if pkg_metadata.remote not in remotes:
                        pkg_metadata.remote = None

        remotes.save(self._filename)