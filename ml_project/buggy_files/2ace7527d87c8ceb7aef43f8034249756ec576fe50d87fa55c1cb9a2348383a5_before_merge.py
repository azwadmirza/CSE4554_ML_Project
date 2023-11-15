    def show_tree(self):
        """Populate the tree with profiler data and display it."""
        self.initialize_view() # Clear before re-populating
        self.setItemsExpandable(True)
        self.setSortingEnabled(False)
        rootkey = self.find_root()  # This root contains profiler overhead
        if rootkey:
            self.populate_tree(self, self.find_callees(rootkey))
            self.resizeColumnToContents(0)
            self.setSortingEnabled(True)
            self.sortItems(1, Qt.AscendingOrder) # FIXME: hardcoded index
            self.change_view(1)