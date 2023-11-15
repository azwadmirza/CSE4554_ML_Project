    def __setitem__(self, key, value):
        """Add the item to the scene."""
        if not isinstance(value, Dataset):
            raise ValueError("Only 'Dataset' objects can be assigned")
        self.datasets[key] = value
        ds_id = self.datasets.get_key(key)
        self.wishlist.add(ds_id)
        self.dep_tree.add_leaf(ds_id)