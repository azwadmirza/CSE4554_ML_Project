    def write_cache(self) -> None:
        assert self.tree is not None, "Internal error: method must be called on parsed file only"
        if not self.path or self.options.cache_dir == os.devnull:
            return
        if self.manager.options.quick_and_dirty:
            is_errors = self.manager.errors.is_errors_for_file(self.path)
        else:
            is_errors = self.manager.errors.is_errors()
        if is_errors:
            return
        dep_prios = [self.priorities.get(dep, PRI_HIGH) for dep in self.dependencies]
        new_interface_hash = write_cache(
            self.id, self.path, self.tree,
            list(self.dependencies), list(self.suppressed), list(self.child_modules),
            dep_prios, self.interface_hash, self.source_hash, self.ignore_all,
            self.manager)
        if new_interface_hash == self.interface_hash:
            self.manager.log("Cached module {} has same interface".format(self.id))
        else:
            self.manager.log("Cached module {} has changed interface".format(self.id))
            self.mark_interface_stale()
            self.interface_hash = new_interface_hash