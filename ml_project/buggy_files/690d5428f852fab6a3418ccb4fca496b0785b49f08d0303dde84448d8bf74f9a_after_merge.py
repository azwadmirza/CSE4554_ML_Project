def assign_particle_data(ds, pdata, bbox):

    """
    Assign particle data to the grids using MatchPointsToGrids. This
    will overwrite any existing particle data, so be careful!
    """

    for ptype in ds.particle_types_raw:
        check_fields = [(ptype, "particle_position_x"),
                        (ptype, "particle_position")]
        if all(f not in pdata for f in check_fields):
            pdata_ftype = {}
            for f in [k for k in sorted(pdata)]:
                if not hasattr(pdata[f], "shape"):
                    continue
                if f == 'number_of_particles':
                    continue
                mylog.debug("Reassigning '%s' to ('%s','%s')", f, ptype, f)
                pdata_ftype[ptype, f] = pdata.pop(f)
            pdata_ftype.update(pdata)
            pdata = pdata_ftype

    # Note: what we need to do here is a bit tricky.  Because occasionally this
    # gets called before we property handle the field detection, we cannot use
    # any information about the index.  Fortunately for us, we can generate
    # most of the GridTree utilizing information we already have from the
    # stream handler.

    if len(ds.stream_handler.fields) > 1:
        pdata.pop("number_of_particles", None)
        num_grids = len(ds.stream_handler.fields)
        parent_ids = ds.stream_handler.parent_ids
        num_children = np.zeros(num_grids, dtype='int64')
        # We're going to do this the slow way
        mask = np.empty(num_grids, dtype="bool")
        for i in range(num_grids):
            np.equal(parent_ids, i, mask)
            num_children[i] = mask.sum()
        levels = ds.stream_handler.levels.astype("int64").ravel()
        grid_tree = GridTree(num_grids,
                             ds.stream_handler.left_edges,
                             ds.stream_handler.right_edges,
                             ds.stream_handler.dimensions,
                             ds.stream_handler.parent_ids,
                             levels, num_children)

        grid_pdata = []
        for i in range(num_grids):
            grid = {"number_of_particles": 0}
            grid_pdata.append(grid)

        for ptype in ds.particle_types_raw:
            if (ptype, "particle_position_x") in pdata:
                x, y, z = (pdata[ptype, "particle_position_%s" % ax] for ax in 'xyz')
            elif (ptype, "particle_position") in pdata:
                x, y, z = pdata[ptype, "particle_position"].T
            else:
                raise KeyError(
                    "Cannot decompose particle data without position fields!")
            pts = MatchPointsToGrids(grid_tree, len(x), x, y, z)
            particle_grid_inds = pts.find_points_in_tree()
            assigned_particles, = (particle_grid_inds >= 0).nonzero()
            num_particles = particle_grid_inds.size
            num_unassigned = num_particles - assigned_particles.size
            if num_unassigned > 0:
                m = ("Discarding %s particles (out of %s) that are outside "
                     "bounding box. ")
                eps = np.finfo(x.dtype).eps
                s = np.array([[x.min() - eps, x.max() + eps],
                              [y.min() - eps, y.max() + eps],
                              [z.min() - eps, z.max() + eps]])
                sug_bbox = [
                    [min(bbox[0, 0], s[0, 0]), max(bbox[0, 1], s[0, 1])],
                    [min(bbox[1, 0], s[1, 0]), max(bbox[1, 1], s[1, 1])],
                    [min(bbox[2, 0], s[2, 0]), max(bbox[2, 1], s[2, 1])]]
                m += ("Set bbox=%s to avoid this in the future.")
                mylog.warn(m % (num_unassigned, num_particles, sug_bbox))
                particle_grid_inds = particle_grid_inds[assigned_particles]
                x = x[assigned_particles]
                y = y[assigned_particles]
                z = z[assigned_particles]
            idxs = np.argsort(particle_grid_inds)
            particle_grid_count = np.bincount(particle_grid_inds.astype("intp"),
                                              minlength=num_grids)
            particle_indices = np.zeros(num_grids + 1, dtype='int64')
            if num_grids > 1:
                np.add.accumulate(particle_grid_count.squeeze(),
                                  out=particle_indices[1:])
            else:
                particle_indices[1] = particle_grid_count.squeeze()
            for i, pcount in enumerate(particle_grid_count):
                grid_pdata[i]["number_of_particles"] += pcount
                start = particle_indices[i]
                end = particle_indices[i+1]
                for key in pdata.keys():
                    if key[0] == ptype:
                        grid_pdata[i][key] = pdata[key][idxs][start:end]

    else:
        grid_pdata = [pdata]

    for pd, gi in zip(grid_pdata, sorted(ds.stream_handler.fields)):
        ds.stream_handler.fields[gi].update(pd)
        ds.stream_handler.particle_types.update(set_particle_types(pd))
        npart = ds.stream_handler.fields[gi].pop("number_of_particles", 0)
        ds.stream_handler.particle_count[gi] = npart