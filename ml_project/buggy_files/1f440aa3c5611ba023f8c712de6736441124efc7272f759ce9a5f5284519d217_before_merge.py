    def get_data(self, element, ranges, style):
        # Get x, y, group, stack and color dimensions
        grouping = None
        group_dim = element.get_dimension(self.group_index)
        if group_dim not in element.kdims:
            group_dim = None
        else:
            grouping = 'grouped'
        stack_dim = element.get_dimension(self.stack_index)
        if stack_dim not in element.kdims:
            stack_dim = None
        else:
            grouping = 'stacked'
            group_dim = None

        xdim = element.get_dimension(0)
        ydim = element.vdims[0]
        no_cidx = self.color_index is None
        color_index = (group_dim or stack_dim) if no_cidx else self.color_index
        color_dim = element.get_dimension(color_index)
        if color_dim:
            self.color_index = color_dim.name

        # Define style information
        width = style.get('width', 1)
        cmap = style.get('cmap')
        hover = any(t == 'hover' or isinstance(t, HoverTool)
                    for t in self.tools+self.default_tools)

        # Group by stack or group dim if necessary
        if group_dim is None:
            grouped = {0: element}
        else:
            grouped = element.groupby(group_dim, group_type=Dataset,
                                      container_type=OrderedDict,
                                      datatype=['dataframe', 'dictionary'])

        y0, y1 = ranges.get(ydim.name, (None, None))
        if self.logy:
            bottom = (ydim.range[0] or (10**(np.log10(y1)-2)) if y1 else 0.01)
        else:
            bottom = 0
        # Map attributes to data
        if grouping == 'stacked':
            mapping = {'x': xdim.name, 'top': 'top',
                       'bottom': 'bottom', 'width': width}
        elif grouping == 'grouped':
            mapping = {'x': 'xoffsets', 'top': ydim.name, 'bottom': bottom,
                       'width': width}
        else:
            mapping = {'x': xdim.name, 'top': ydim.name, 'bottom': bottom, 'width': width}

        # Get colors
        cdim = color_dim or group_dim
        cvals = element.dimension_values(cdim, expanded=False) if cdim else None
        if cvals is not None:
            if cvals.dtype.kind in 'uif' and no_cidx:
                cvals = categorize_array(cvals, color_dim)

            factors = None if cvals.dtype.kind in 'uif' else list(cvals)
            if cdim is xdim and factors:
                factors = list(categorize_array(factors, xdim))
            if cmap is None and factors:
                styles = self.style.max_cycles(len(factors))
                colors = [styles[i]['color'] for i in range(len(factors))]
                colors = [rgb2hex(c) if isinstance(c, tuple) else c for c in colors]
            else:
                colors = None
        else:
            factors, colors = None, None

        # Iterate over stacks and groups and accumulate data
        data = defaultdict(list)
        baselines = defaultdict(lambda: {'positive': bottom, 'negative': 0})
        for i, (k, ds) in enumerate(grouped.items()):
            k = k[0] if isinstance(k, tuple) else k
            if group_dim:
                gval = k if isinstance(k, basestring) else group_dim.pprint_value(k)
            # Apply stacking or grouping
            if grouping == 'stacked':
                for sign, slc in [('negative', (None, 0)), ('positive', (0, None))]:
                    slc_ds = ds.select(**{ds.vdims[0].name: slc})
                    xs = slc_ds.dimension_values(xdim)
                    ys = slc_ds.dimension_values(ydim)
                    bs, ts = self.get_stack(xs, ys, baselines, sign)
                    data['bottom'].append(bs)
                    data['top'].append(ts)
                    data[xdim.name].append(xs)
                    data[stack_dim.name].append(slc_ds.dimension_values(stack_dim))
                    if hover: data[ydim.name].append(ys)
                    self._add_color_data(slc_ds, ranges, style, cdim, data,
                                         mapping, factors, colors)
            elif grouping == 'grouped':
                xs = ds.dimension_values(xdim)
                ys = ds.dimension_values(ydim)
                xoffsets = [(x if xs.dtype.kind in 'SU' else xdim.pprint_value(x), gval)
                            for x in xs]
                data['xoffsets'].append(xoffsets)
                data[ydim.name].append(ys)
                if hover: data[xdim.name].append(xs)
                if group_dim not in ds.dimensions():
                    ds = ds.add_dimension(group_dim.name, ds.ndims, gval)
                data[group_dim.name].append(ds.dimension_values(group_dim))
            else:
                data[xdim.name].append(ds.dimension_values(xdim))
                data[ydim.name].append(ds.dimension_values(ydim))

            if hover:
                for vd in ds.vdims[1:]:
                    data[vd.name].append(ds.dimension_values(vd))

            if not grouping == 'stacked':
                self._add_color_data(ds, ranges, style, cdim, data,
                                     mapping, factors, colors)

        # Concatenate the stacks or groups
        sanitized_data = {}
        for col, vals in data.items():
            if len(vals) == 1:
                sanitized_data[dimension_sanitizer(col)] = vals[0]
            elif vals:
                sanitized_data[dimension_sanitizer(col)] = np.concatenate(vals)

        for name, val in mapping.items():
            sanitized = None
            if isinstance(val, basestring):
                sanitized = dimension_sanitizer(mapping[name])
                mapping[name] = sanitized
            elif isinstance(val, dict) and 'field' in val:
                sanitized = dimension_sanitizer(val['field'])
                val['field'] = sanitized
            if sanitized is not None and sanitized not in sanitized_data:
                sanitized_data[sanitized] = []

        # Ensure x-values are categorical
        xname = dimension_sanitizer(xdim.name)
        if xname in sanitized_data:
            sanitized_data[xname] = categorize_array(sanitized_data[xname], xdim)

        # If axes inverted change mapping to match hbar signature
        if self.invert_axes:
            mapping.update({'y': mapping.pop('x'), 'left': mapping.pop('bottom'),
                            'right': mapping.pop('top'), 'height': mapping.pop('width')})

        return sanitized_data, mapping, style