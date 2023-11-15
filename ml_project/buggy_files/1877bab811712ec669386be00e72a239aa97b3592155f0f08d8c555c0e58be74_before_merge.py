    def _generate_composite(self, comp_node, keepables):
        """Collect all composite prereqs and create the specified composite.

        Args:
            comp_node (Node): Composite Node to generate a Dataset for
            keepables (set): `set` to update if any datasets are needed
                             when generation is continued later. This can
                             happen if generation is delayed to incompatible
                             areas which would require resampling first.

        """
        if comp_node.name in self.datasets:
            # already loaded
            return
        compositor, prereqs, optional_prereqs = comp_node.data

        try:
            prereq_datasets = self._get_prereq_datasets(
                comp_node.name,
                prereqs,
                keepables,
            )
        except KeyError:
            return

        optional_datasets = self._get_prereq_datasets(
            comp_node.name,
            optional_prereqs,
            keepables,
            skip=True
        )

        try:
            composite = compositor(prereq_datasets,
                                   optional_datasets=optional_datasets,
                                   **self.info)
            self.datasets[composite.id] = composite
            if comp_node.name in self.wishlist:
                self.wishlist.remove(comp_node.name)
                self.wishlist.add(composite.id)
            # update the node with the computed DatasetID
            comp_node.name = composite.id
        except IncompatibleAreas:
            LOG.warning("Delaying generation of %s "
                        "because of incompatible areas",
                        str(compositor.id))
            preservable_datasets = set(self.datasets.keys())
            prereq_ids = set(p.name for p in prereqs)
            opt_prereq_ids = set(p.name for p in optional_prereqs)
            keepables |= preservable_datasets & (prereq_ids | opt_prereq_ids)
            # even though it wasn't generated keep a list of what
            # might be needed in other compositors
            keepables.add(comp_node.name)
            return