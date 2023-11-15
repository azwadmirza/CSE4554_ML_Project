    def _find_compositor(self, dataset_key, calibration=None, polarization=None, resolution=None):
        """Find the compositor object for the given dataset_key."""
        # NOTE: This function can not find a modifier that performs one or more modifications
        # if it has modifiers see if we can find the unmodified version first
        src_node = None
        if isinstance(dataset_key, DatasetID) and dataset_key.modifiers:
            new_prereq = DatasetID(
                *dataset_key[:-1] + (dataset_key.modifiers[:-1],))
            src_node, u = self._find_dependencies(new_prereq, calibration, polarization, resolution)
            if u:
                return None, u

        try:
            compositor = self.get_compositor(dataset_key)
        except KeyError:
            raise KeyError("Can't find anything called {}".format(
                str(dataset_key)))
        if resolution:
            compositor.info['resolution'] = resolution
        if calibration:
            compositor.info['calibration'] = calibration
        if polarization:
            compositor.info['polarization'] = polarization
        dataset_key = compositor.id
        # 2.1 get the prerequisites
        prereqs, unknowns = self._get_compositor_prereqs(
            compositor.info['prerequisites'], calibration=calibration, polarization=polarization, resolution=resolution)
        if unknowns:
            return None, unknowns

        optional_prereqs, _ = self._get_compositor_prereqs(
            compositor.info['optional_prerequisites'],
            skip=True, calibration=calibration, polarization=polarization, resolution=resolution)

        # Is this the right place for that?
        if src_node is not None:
            prereqs.insert(0, src_node)
        root = Node(dataset_key, data=(compositor, prereqs, optional_prereqs))
        # LOG.debug("Found composite {}".format(str(dataset_key)))
        for prereq in prereqs + optional_prereqs:
            if prereq is not None:
                self.add_child(root, prereq)

        return root, set()