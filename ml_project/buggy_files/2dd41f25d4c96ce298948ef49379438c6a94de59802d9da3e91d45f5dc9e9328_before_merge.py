    def mark_interface_stale(self) -> None:
        """Marks this module as having a stale public interface, and discards the cache data."""
        self.meta = None
        self.externally_same = False
        self.manager.stale_modules.add(self.id)