    def download_packages(self, reference, package_ids):
        assert(isinstance(package_ids, list))
        remote, _ = self._get_remote(reference)
        export_path = self._client_cache.export(reference)
        self._remote_manager.get_recipe(reference, export_path, remote)
        self._registry.set_ref(reference, remote)
        output = ScopedOutput(str(reference), self._out)
        for package_id in package_ids:
            package_reference = PackageReference(reference, package_id)
            self._retrieve_remote_package(package_reference, output, remote)