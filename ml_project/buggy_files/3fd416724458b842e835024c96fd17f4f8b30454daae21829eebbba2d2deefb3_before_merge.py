    def add(self, remote_name, url, verify_ssl=True, insert=None, force=None):
        self._validate_url(url)
        remotes = self.load_remotes()
        renamed = remotes.add(remote_name, url, verify_ssl, insert, force)
        remotes.save(self._filename)
        if renamed:
            for ref in self._cache.all_refs():
                with self._cache.package_layout(ref).update_metadata() as metadata:
                    if metadata.recipe.remote == renamed:
                        metadata.recipe.remote = remote_name
                    for pkg_metadata in metadata.packages.values():
                        if pkg_metadata.remote == renamed:
                            pkg_metadata.remote = remote_name