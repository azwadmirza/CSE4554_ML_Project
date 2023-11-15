    def ensure_directories(self):
        dirs = {self.dest_dir, self.bin_dir, self.lib_dir}
        dirs.update(self.site_packages)
        return dirs