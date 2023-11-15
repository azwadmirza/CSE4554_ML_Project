    def update_folding(self, ranges):
        """Update folding panel folding ranges."""
        if ranges is None:
            return

        self.current_tree, self.root = merge_folding(
            ranges, self.current_tree, self.root)

        folding_info = collect_folding_regions(self.root)

        (self.folding_regions, self.folding_nesting,
         self.folding_levels, self.folding_status) = folding_info
        self.update()