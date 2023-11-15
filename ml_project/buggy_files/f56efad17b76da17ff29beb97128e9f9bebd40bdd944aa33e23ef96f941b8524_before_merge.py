    def update_metadata(self):
        lockfile = self.package_metadata() + ".lock"
        with fasteners.InterProcessLock(lockfile, logger=logger):
            try:
                metadata = self.load_metadata()
            except RecipeNotFoundException:
                metadata = PackageMetadata()
            yield metadata
            save(self.package_metadata(), metadata.dumps())