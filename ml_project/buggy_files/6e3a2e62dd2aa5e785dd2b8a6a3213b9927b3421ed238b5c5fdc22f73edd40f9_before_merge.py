    def resample(self,
                 destination,
                 datasets=None,
                 compute=True,
                 unload=True,
                 **resample_kwargs):
        """Resample the datasets and return a new scene.
        """
        new_scn = Scene()
        new_scn.info = self.info.copy()
        # new_scn.cpl = self.cpl
        new_scn.dep_tree = self.dep_tree.copy()
        for ds_id, projectable in self.datasets.items():
            LOG.debug("Resampling %s", ds_id)
            if datasets and ds_id not in datasets:
                continue
            new_scn[ds_id] = projectable.resample(destination,
                                                  **resample_kwargs)
        # MUST set this after assigning the resampled datasets otherwise
        # composite prereqs that were resampled will be considered "wishlisted"
        if datasets is None:
            new_scn.wishlist = self.wishlist
        else:
            new_scn.wishlist = set([ds.id for ds in new_scn])

        # recompute anything from the wishlist that needs it (combining multiple
        # resolutions, etc.)
        keepables = None
        if compute:
            nodes = [self.dep_tree[i]
                     for i in new_scn.wishlist if not self.dep_tree[i].is_leaf]
            keepables = new_scn.compute(nodes=nodes)
        if new_scn.missing_datasets:
            # copy the set of missing datasets because they won't be valid
            # after they are removed in the next line
            missing = new_scn.missing_datasets.copy()
            new_scn._remove_failed_datasets(keepables)
            missing_str = ", ".join(str(x) for x in missing)
            LOG.warning(
                "The following datasets were not created: {}".format(missing_str))
        if unload:
            new_scn.unload(keepables)

        return new_scn