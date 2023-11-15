    def package_id_exists(self, package_id):
        # The package exists if the folder exists, also for short_paths case
        pkg_folder = self.package(PackageReference(self._ref, package_id))
        return os.path.isdir(pkg_folder)