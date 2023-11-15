    def available_composite_ids(self, available_datasets=None):
        """Get names of compositors that can be generated from the available
        datasets.

        :return: generator of available compositor's names
        """
        if available_datasets is None:
            available_datasets = self.available_dataset_ids(composites=False)
        else:
            if not all(isinstance(ds_id, DatasetID) for ds_id in available_datasets):
                raise ValueError(
                    "'available_datasets' must all be DatasetID objects")

        all_comps = self.all_composite_ids()
        # recreate the dependency tree so it doesn't interfere with the user's
        # wishlist
        comps, mods = self.cpl.load_compositors(self.attrs['sensor'])
        dep_tree = DependencyTree(self.readers, comps, mods)
        unknowns = dep_tree.find_dependencies(
            set(available_datasets + all_comps))
        available_comps = set(x.name for x in dep_tree.trunk())
        # get rid of modified composites that are in the trunk
        return sorted(available_comps & set(all_comps))