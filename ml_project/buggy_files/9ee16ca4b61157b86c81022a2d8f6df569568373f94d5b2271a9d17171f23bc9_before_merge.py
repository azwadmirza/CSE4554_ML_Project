def load_uniform_grid(data, domain_dimensions, length_unit=None, bbox=None,
                      nprocs=1, sim_time=0.0, mass_unit=None, time_unit=None,
                      velocity_unit=None, magnetic_unit=None,
                      periodicity=(True, True, True),
                      geometry="cartesian", unit_system="cgs"):
    r"""Load a uniform grid of data into yt as a
    :class:`~yt.frontends.stream.data_structures.StreamHandler`.

    This should allow a uniform grid of data to be loaded directly into yt and
    analyzed as would any others.  This comes with several caveats:

    * Units will be incorrect unless the unit system is explicitly
      specified.
    * Some functions may behave oddly, and parallelism will be
      disappointing or non-existent in most cases.
    * Particles may be difficult to integrate.

    Particle fields are detected as one-dimensional fields.

    Parameters
    ----------
    data : dict
        This is a dict of numpy arrays or (numpy array, unit spec) tuples.
        The keys are the field names.
    domain_dimensions : array_like
        This is the domain dimensions of the grid
    length_unit : string
        Unit to use for lengths.  Defaults to unitless.
    bbox : array_like (xdim:zdim, LE:RE), optional
        Size of computational domain in units specified by length_unit.
        Defaults to a cubic unit-length domain.
    nprocs: integer, optional
        If greater than 1, will create this number of subarrays out of data
    sim_time : float, optional
        The simulation time in seconds
    mass_unit : string
        Unit to use for masses.  Defaults to unitless.
    time_unit : string
        Unit to use for times.  Defaults to unitless.
    velocity_unit : string
        Unit to use for velocities.  Defaults to unitless.
    magnetic_unit : string
        Unit to use for magnetic fields. Defaults to unitless.
    periodicity : tuple of booleans
        Determines whether the data will be treated as periodic along
        each axis
    geometry : string or tuple
        "cartesian", "cylindrical", "polar", "spherical", "geographic" or
        "spectral_cube".  Optionally, a tuple can be provided to specify the
        axis ordering -- for instance, to specify that the axis ordering should
        be z, x, y, this would be: ("cartesian", ("z", "x", "y")).  The same
        can be done for other coordinates, for instance:
        ("spherical", ("theta", "phi", "r")).

    Examples
    --------

    >>> bbox = np.array([[0., 1.0], [-1.5, 1.5], [1.0, 2.5]])
    >>> arr = np.random.random((128, 128, 128))

    >>> data = dict(density=arr)
    >>> ds = load_uniform_grid(data, arr.shape, length_unit='cm',
    ...                        bbox=bbox, nprocs=12)
    >>> dd = ds.all_data()
    >>> dd['density']

    YTArray([ 0.87568064,  0.33686453,  0.70467189, ...,  0.70439916,
            0.97506269,  0.03047113]) g/cm**3

    >>> data = dict(density=(arr, 'kg/m**3'))
    >>> ds = load_uniform_grid(data, arr.shape, length_unit=3.03e24,
    ...                        bbox=bbox, nprocs=12)
    >>> dd = ds.all_data()
    >>> dd['density']

    YTArray([  8.75680644e-04,   3.36864527e-04,   7.04671886e-04, ...,
             7.04399160e-04,   9.75062693e-04,   3.04711295e-05]) g/cm**3

    """

    domain_dimensions = np.array(domain_dimensions)
    if bbox is None:
        bbox = np.array([[0.0, 1.0], [0.0, 1.0], [0.0, 1.0]], 'float64')
    domain_left_edge = np.array(bbox[:, 0], 'float64')
    domain_right_edge = np.array(bbox[:, 1], 'float64')
    grid_levels = np.zeros(nprocs, dtype='int32').reshape((nprocs,1))
    # If someone included this throw it away--old API
    if "number_of_particles" in data:
        issue_deprecation_warning("It is no longer necessary to include "
                                  "the number of particles in the data "
                                  "dict. The number of particles is "
                                  "determined from the sizes of the "
                                  "particle fields.")
        data.pop("number_of_particles")
    # First we fix our field names, apply units to data
    # and check for consistency of field shapes
    field_units, data, number_of_particles = process_data(
        data, grid_dims=tuple(domain_dimensions))

    sfh = StreamDictFieldHandler()

    if number_of_particles > 0:
        particle_types = set_particle_types(data)
        # Used much further below.
        pdata = {"number_of_particles": number_of_particles}
        for key in list(data.keys()):
            if len(data[key].shape) == 1 or key[0] == 'io':
                if not isinstance(key, tuple):
                    field = ("io", key)
                    mylog.debug("Reassigning '%s' to '%s'", key, field)
                else:
                    field = key
                sfh._additional_fields += (field,)
                pdata[field] = data.pop(key)
    else:
        particle_types = {}

    if nprocs > 1:
        temp = {}
        new_data = {}
        for key in data.keys():
            psize = get_psize(np.array(data[key].shape), nprocs)
            grid_left_edges, grid_right_edges, shapes, slices = \
                             decompose_array(data[key].shape, psize, bbox)
            grid_dimensions = np.array([shape for shape in shapes],
                                       dtype="int32")
            temp[key] = [data[key][slice] for slice in slices]
        for gid in range(nprocs):
            new_data[gid] = {}
            for key in temp.keys():
                new_data[gid].update({key:temp[key][gid]})
        sfh.update(new_data)
        del new_data, temp
    else:
        sfh.update({0:data})
        grid_left_edges = domain_left_edge
        grid_right_edges = domain_right_edge
        grid_dimensions = domain_dimensions.reshape(nprocs, 3).astype("int32")

    if length_unit is None:
        length_unit = 'code_length'
    if mass_unit is None:
        mass_unit = 'code_mass'
    if time_unit is None:
        time_unit = 'code_time'
    if velocity_unit is None:
        velocity_unit = 'code_velocity'
    if magnetic_unit is None:
        magnetic_unit = 'code_magnetic'

    handler = StreamHandler(
        grid_left_edges,
        grid_right_edges,
        grid_dimensions,
        grid_levels,
        -np.ones(nprocs, dtype='int64'),
        np.zeros(nprocs, dtype='int64').reshape(nprocs,1), # particle count
        np.zeros(nprocs).reshape((nprocs,1)),
        sfh,
        field_units,
        (length_unit, mass_unit, time_unit, velocity_unit, magnetic_unit),
        particle_types=particle_types,
        periodicity=periodicity
    )

    handler.name = "UniformGridData"
    handler.domain_left_edge = domain_left_edge
    handler.domain_right_edge = domain_right_edge
    handler.refine_by = 2
    if np.all(domain_dimensions[1:] == 1):
        dimensionality = 1
    elif domain_dimensions[2] == 1:
        dimensionality = 2
    else:
        dimensionality = 3
    handler.dimensionality = dimensionality
    handler.domain_dimensions = domain_dimensions
    handler.simulation_time = sim_time
    handler.cosmology_simulation = 0

    sds = StreamDataset(handler, geometry=geometry, unit_system=unit_system)

    # Now figure out where the particles go
    if number_of_particles > 0:
        # This will update the stream handler too
        assign_particle_data(sds, pdata)

    return sds