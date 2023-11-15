    def inventory(self):
        """Starting from the given file, try to cache as much existence and
        modification date information of this and other files as possible.
        """
        cache = self.rule.workflow.iocache
        if cache.active and cache.needs_inventory(self):
            if self.is_remote:
                # info not yet in inventory, let's discover as much as we can
                self.remote_object.inventory(cache)
            elif not ON_WINDOWS:
                # we don't want to mess with different path representations on windows
                self._local_inventory(cache)