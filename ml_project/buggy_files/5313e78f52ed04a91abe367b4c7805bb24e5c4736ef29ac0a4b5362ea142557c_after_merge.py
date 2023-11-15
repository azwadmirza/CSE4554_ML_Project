    def inventory(self):
        """Starting from the given file, try to cache as much existence and
        modification date information of this and other files as possible.
        """
        cache = self.rule.workflow.iocache
        if (
            cache.active
            and not self.inventory_path is None
            and cache.needs_inventory(self.inventory_root)
        ):
            # info not yet in inventory, let's discover as much as we can
            if self.is_remote:
                self.remote_object.inventory(cache)
            else:
                self._local_inventory(cache)