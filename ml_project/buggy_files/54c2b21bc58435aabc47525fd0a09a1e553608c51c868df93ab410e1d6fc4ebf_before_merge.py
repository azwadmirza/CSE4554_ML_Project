    def package_id_exists(self, package_id):
        # This is NOT the short paths, but the standard cache one
        pkg_folder = os.path.join(self._base_folder, PACKAGES_FOLDER, package_id)
        return os.path.isdir(pkg_folder)