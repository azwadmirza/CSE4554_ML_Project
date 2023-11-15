    def update_after_read_foreign_file(self, root):
        """Restore gnx's, uAs and clone links using @gnxs nodes and @uas trees."""
        self.at_persistence = self.find_at_persistence_node()
        if not self.at_persistence:
            return
        if not self.is_foreign_file(root):
            return
        # Create clone links from @gnxs node
        at_gnxs = self.has_at_gnxs_node(root)
        if at_gnxs:
            self.restore_gnxs(at_gnxs, root)
        # Create uas from @uas tree.
        at_uas = self.has_at_uas_node(root)
        if at_uas:
            self.create_uas(at_uas, root)