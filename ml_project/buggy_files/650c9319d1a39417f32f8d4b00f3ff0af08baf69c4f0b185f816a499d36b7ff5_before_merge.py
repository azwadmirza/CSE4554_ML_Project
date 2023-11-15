    def search_packages(self, reference=None, remote=None, query=None, outdated=False):
        """ Return the single information saved in conan.vars about all the packages
            or the packages which match with a pattern

            Attributes:
                pattern = string to match packages
                remote = search on another origin to get packages info
                packages_pattern = String query with binary
                                   packages properties: "arch=x86 AND os=Windows"
        """
        if remote:
            remote = RemoteRegistry(self._client_cache.registry, self._user_io).remote(remote)
            packages_props = self._remote_manager.search_packages(remote, reference, query)
            ordered_packages = OrderedDict(sorted(packages_props.items()))
            manifest = self._remote_manager.get_conan_digest(reference, remote)
            recipe_hash = manifest.summary_hash
        else:
            searcher = DiskSearchManager(self._client_cache)
            packages_props = searcher.search_packages(reference, query)
            ordered_packages = OrderedDict(sorted(packages_props.items()))
            try:
                recipe_hash = self._client_cache.load_manifest(reference).summary_hash
            except IOError:  # It could not exist in local
                recipe_hash = None
        if outdated and recipe_hash:
            ordered_packages = filter_outdated(ordered_packages, recipe_hash)
        return ordered_packages, reference, recipe_hash, query