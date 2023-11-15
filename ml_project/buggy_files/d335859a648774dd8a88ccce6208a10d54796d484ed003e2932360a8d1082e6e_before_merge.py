    def remove(self, remote_name):
        remotes = self.load_remotes()
        del remotes[remote_name]

        for ref in self._cache.all_refs():
            with self._cache.package_layout(ref).update_metadata() as metadata:
                if metadata.recipe.remote == remote_name:
                    metadata.recipe.remote = None
                for pkg_metadata in metadata.packages.values():
                    if pkg_metadata.remote == remote_name:
                        pkg_metadata.remote = None

        remotes.save(self._filename)