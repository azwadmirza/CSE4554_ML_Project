    def clear(self):
        remotes = self.load_remotes()
        remotes.clear()
        with self._cache.editable_packages.disable_editables():
            for ref in self._cache.all_refs():
                with self._cache.package_layout(ref).update_metadata() as metadata:
                    metadata.recipe.remote = None
                    for pkg_metadata in metadata.packages.values():
                        pkg_metadata.remote = None
            remotes.save(self._filename)