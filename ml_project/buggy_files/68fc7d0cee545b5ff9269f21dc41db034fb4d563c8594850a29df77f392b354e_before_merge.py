    def _compute_group_range(cls, group, elements, ranges, framewise, top_level):
        # Iterate over all elements in a normalization group
        # and accumulate their ranges into the supplied dictionary.
        elements = [el for el in elements if el is not None]
        prev_ranges = ranges.get(group, {})
        group_ranges = OrderedDict()
        for el in elements:
            if isinstance(el, (Empty, Table)): continue
            opts = cls.lookup_options(el, 'style')
            plot_opts = cls.lookup_options(el, 'plot')

            # Compute normalization for color dim transforms
            for k, v in dict(opts.kwargs, **plot_opts.kwargs).items():
                if not isinstance(v, dim) or ('color' not in k and k != 'magnitude'):
                    continue

                if isinstance(v, dim) and v.applies(el):
                    dim_name = repr(v)
                    if dim_name in prev_ranges and not framewise:
                        continue
                    values = v.apply(el, expanded=False, all_values=True)
                    factors = None
                    if values.dtype.kind == 'M':
                        drange = values.min(), values.max()
                    elif util.isscalar(values):
                        drange = values, values
                    elif len(values) == 0:
                        drange = np.NaN, np.NaN
                    else:
                        try:
                            with warnings.catch_warnings():
                                warnings.filterwarnings('ignore', r'All-NaN (slice|axis) encountered')
                                drange = (np.nanmin(values), np.nanmax(values))
                        except:
                            factors = util.unique_array(values)
                    if dim_name not in group_ranges:
                        group_ranges[dim_name] = {'data': [], 'hard': [], 'soft': []}
    
                    if factors is not None:
                        if 'factors' not in group_ranges[dim_name]:
                            group_ranges[dim_name]['factors'] = []
                        group_ranges[dim_name]['factors'].append(factors)
                    else:
                        group_ranges[dim_name]['data'].append(drange)

            # Compute dimension normalization
            for el_dim in el.dimensions('ranges'):
                dim_name = el_dim.name
                if dim_name in prev_ranges and not framewise:
                    continue
                if hasattr(el, 'interface'):
                    if isinstance(el, Graph) and el_dim in el.nodes.dimensions():
                        dtype = el.nodes.interface.dtype(el.nodes, el_dim)
                    elif isinstance(el, Contours) and el.level is not None:
                        dtype = np.array([el.level]).dtype # Remove when deprecating level
                    else:
                        dtype = el.interface.dtype(el, el_dim)
                else:
                    dtype = None

                if all(util.isfinite(r) for r in el_dim.range):
                    data_range = (None, None)
                elif dtype is not None and dtype.kind in 'SU':
                    data_range = ('', '')
                elif isinstance(el, Graph) and el_dim in el.kdims[:2]:
                    data_range = el.nodes.range(2, dimension_range=False)
                elif el_dim.values:
                    ds = Dataset(el_dim.values, el_dim)
                    data_range = ds.range(el_dim, dimension_range=False)
                else:
                    data_range = el.range(el_dim, dimension_range=False)

                if dim_name not in group_ranges:
                    group_ranges[dim_name] = {'data': [], 'hard': [], 'soft': []}
                group_ranges[dim_name]['data'].append(data_range)
                group_ranges[dim_name]['hard'].append(el_dim.range)
                group_ranges[dim_name]['soft'].append(el_dim.soft_range)
                if (any(isinstance(r, util.basestring) for r in data_range) or
                    el_dim.type is not None and issubclass(el_dim.type, util.basestring)):
                    if 'factors' not in group_ranges[dim_name]:
                        group_ranges[dim_name]['factors'] = []
                    if el_dim.values not in ([], None):
                        values = el_dim.values
                    elif el_dim in el:
                        if isinstance(el, Graph) and el_dim in el.kdims[:2]:
                            # Graph start/end normalization should include all node indices
                            values = el.nodes.dimension_values(2, expanded=False)
                        else:
                            values = el.dimension_values(el_dim, expanded=False)
                    elif isinstance(el, Graph) and el_dim in el.nodes:
                        values = el.nodes.dimension_values(el_dim, expanded=False)
                    if (isinstance(values, np.ndarray) and values.dtype.kind == 'O' and
                        all(isinstance(v, (np.ndarray)) for v in values)):
                        values = np.concatenate(values)
                    factors = util.unique_array(values)
                    group_ranges[dim_name]['factors'].append(factors)

        group_dim_ranges = defaultdict(dict)
        for gdim, values in group_ranges.items():
            matching = True
            for t, rs in values.items():
                if t == 'factors':
                    continue
                matching &= (
                    len({'date' if isinstance(v, util.datetime_types) else 'number'
                         for rng in rs for v in rng if util.isfinite(v)}) < 2
                )
            if matching:
                group_dim_ranges[gdim] = values

        dim_ranges = []
        for gdim, values in group_dim_ranges.items():
            hard_range = util.max_range(values['hard'], combined=False)
            soft_range = util.max_range(values['soft'])
            data_range = util.max_range(values['data'])
            combined = util.dimension_range(data_range[0], data_range[1],
                                            hard_range, soft_range)
            dranges = {'data': data_range, 'hard': hard_range,
                       'soft': soft_range, 'combined': combined}
            if 'factors' in values:
                dranges['factors'] = util.unique_array([
                    v for fctrs in values['factors'] for v in fctrs])
            dim_ranges.append((gdim, dranges))
        if prev_ranges and not (framewise and top_level):
            for d, dranges in dim_ranges:
                for g, drange in dranges.items():
                    prange = prev_ranges.get(d, {}).get(g, None)
                    if prange is None:
                        if d not in prev_ranges:
                            prev_ranges[d] = {}
                        prev_ranges[d][g] = drange
                    else:
                        prev_ranges[d][g] = util.max_range([drange, prange],
                                                           combined=g=='hard')            
        else:
            ranges[group] = OrderedDict(dim_ranges)