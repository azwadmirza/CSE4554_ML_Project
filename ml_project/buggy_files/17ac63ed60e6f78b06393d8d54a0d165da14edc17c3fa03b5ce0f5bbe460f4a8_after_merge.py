    def resample(self,
                 destination=None,
                 datasets=None,
                 compute=True,
                 unload=True,
                 **resample_kwargs):
        """Resample the datasets and return a new scene."""
        to_resample = [dataset for (dsid, dataset) in self.datasets.items()
                       if (not datasets) or dsid in datasets]

        if destination is None:
            destination = self.max_area(to_resample)
        new_scn = self._resampled_scene(to_resample, destination,
                                        **resample_kwargs)

        new_scn.attrs = self.attrs.copy()
        new_scn.dep_tree = self.dep_tree.copy()

        # MUST set this after assigning the resampled datasets otherwise
        # composite prereqs that were resampled will be considered "wishlisted"
        if datasets is None:
            new_scn.wishlist = self.wishlist.copy()
        else:
            new_scn.wishlist = set([DatasetID.from_dict(ds.attrs)
                                    for ds in new_scn])

        # recompute anything from the wishlist that needs it (combining
        # multiple resolutions, etc.)
        keepables = None
        if compute:
            nodes = [self.dep_tree[i]
                     for i in new_scn.wishlist
                     if i in self.dep_tree and not self.dep_tree[i].is_leaf]
            keepables = new_scn.compute(nodes=nodes)
        if new_scn.missing_datasets:
            # copy the set of missing datasets because they won't be valid
            # after they are removed in the next line
            missing = new_scn.missing_datasets.copy()
            new_scn._remove_failed_datasets(keepables)
            missing_str = ", ".join(str(x) for x in missing)
            LOG.warning(
                "The following datasets "
                "were not created: {}".format(missing_str))
        if unload:
            new_scn.unload(keepables)

        return new_scn