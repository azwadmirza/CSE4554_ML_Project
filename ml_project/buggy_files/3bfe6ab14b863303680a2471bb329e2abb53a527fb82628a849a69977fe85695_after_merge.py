    def __setitem__(self, key, value):
        """Add the item to the scene."""
        self.datasets[key] = value
        ds_id = self.datasets.get_key(key)
        self.wishlist.add(ds_id)
        self.dep_tree.add_leaf(ds_id)