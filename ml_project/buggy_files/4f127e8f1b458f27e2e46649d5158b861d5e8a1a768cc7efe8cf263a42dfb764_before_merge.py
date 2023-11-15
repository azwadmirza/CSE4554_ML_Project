def refine_amr(base_ds, refinement_criteria, fluid_operators, max_level,
               callback=None):
    r"""Given a base dataset, repeatedly apply refinement criteria and
    fluid operators until a maximum level is reached.

    Parameters
    ----------
    base_ds : ~yt.data_objects.static_output.Dataset
        This is any static output.  It can also be a stream static output, for
        instance as returned by load_uniform_data.
    refinement_critera : list of :class:`~yt.utilities.flagging_methods.FlaggingMethod`
        These criteria will be applied in sequence to identify cells that need
        to be refined.
    fluid_operators : list of :class:`~yt.utilities.initial_conditions.FluidOperator`
        These fluid operators will be applied in sequence to all resulting
        grids.
    max_level : int
        The maximum level to which the data will be refined
    callback : function, optional
        A function that will be called at the beginning of each refinement
        cycle, with the current dataset.

    Examples
    --------
    >>> domain_dims = (32, 32, 32)
    >>> data = np.zeros(domain_dims) + 0.25
    >>> fo = [ic.CoredSphere(0.05, 0.3, [0.7,0.4,0.75], {"Density": (0.25, 100.0)})]
    >>> rc = [fm.flagging_method_registry["overdensity"](8.0)]
    >>> ug = load_uniform_grid({'Density': data}, domain_dims, 1.0)
    >>> ds = refine_amr(ug, rc, fo, 5)
    """

    # If we have particle data, set it aside for now

    number_of_particles = np.sum([grid.NumberOfParticles
                                  for grid in base_ds.index.grids])

    if number_of_particles > 0:
        pdata = {}
        for field in base_ds.field_list:
            if not isinstance(field, tuple):
                field = ("unknown", field)
            fi = base_ds._get_field_info(*field)
            if fi.particle_type and field[0] in base_ds.particle_types_raw:
                pdata[field] = uconcatenate([grid[field]
                                             for grid in base_ds.index.grids])
        pdata["number_of_particles"] = number_of_particles

    last_gc = base_ds.index.num_grids
    cur_gc = -1
    ds = base_ds
    bbox = np.array([(ds.domain_left_edge[i], ds.domain_right_edge[i])
                     for i in range(3)])
    while ds.index.max_level < max_level and last_gc != cur_gc:
        mylog.info("Refining another level.  Current max level: %s",
                  ds.index.max_level)
        last_gc = ds.index.grids.size
        for m in fluid_operators: m.apply(ds)
        if callback is not None: callback(ds)
        grid_data = []
        for g in ds.index.grids:
            gd = dict(left_edge=g.LeftEdge,
                       right_edge=g.RightEdge,
                       level=g.Level,
                       dimensions=g.ActiveDimensions)
            for field in ds.field_list:
                if not isinstance(field, tuple):
                    field = ("unknown", field)
                fi = ds._get_field_info(*field)
                if not fi.particle_type:
                    gd[field] = g[field]
            grid_data.append(gd)
            if g.Level < ds.index.max_level: continue
            fg = FlaggingGrid(g, refinement_criteria)
            nsg = fg.find_subgrids()
            for sg in nsg:
                LE = sg.left_index * g.dds + ds.domain_left_edge
                dims = sg.dimensions * ds.refine_by
                grid = ds.smoothed_covering_grid(g.Level + 1, LE, dims)
                gd = dict(left_edge=LE, right_edge=grid.right_edge,
                          level=g.Level + 1, dimensions=dims)
                for field in ds.field_list:
                    if not isinstance(field, tuple):
                        field = ("unknown", field)
                    fi = ds._get_field_info(*field)
                    if not fi.particle_type:
                        gd[field] = grid[field]
                grid_data.append(gd)

        ds = load_amr_grids(grid_data, ds.domain_dimensions, bbox=bbox)

        ds.particle_types_raw = base_ds.particle_types_raw
        ds.particle_types = ds.particle_types_raw

        # Now figure out where the particles go
        if number_of_particles > 0:
            # This will update the stream handler too
            assign_particle_data(ds, pdata)

        cur_gc = ds.index.num_grids

    return ds