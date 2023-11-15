    def get_data(self, element, ranges, style):
        if element.kdims:
            groups = element.groupby(element.kdims).data
        else:
            groups = dict([(element.label, element)])
        vdim = dimension_sanitizer(element.vdims[0].name)

        # Define CDS data
        r1_data, r2_data = ({'index': [], 'top': [], 'bottom': []} for i in range(2))
        s1_data, s2_data = ({'x0': [], 'y0': [], 'x1': [], 'y1': []} for i in range(2))
        w1_data, w2_data = ({'index': [], vdim: []} for i in range(2))
        out_data = defaultdict(list, {'index': [], vdim: []})

        # Define glyph-data mapping
        width = style.get('box_width', style.get('width', 0.7))
        if self.invert_axes:
            vbar_map = {'y': 'index', 'left': 'top', 'right': 'bottom', 'height': width}
            seg_map = {'y0': 'x0', 'y1': 'x1', 'x0': 'y0', 'x1': 'y1'}
            whisk_map = {'y': 'index', 'x': vdim, 'height': 0.2, 'width': 0.001}
            out_map = {'y': 'index', 'x': vdim}
        else:
            vbar_map = {'x': 'index', 'top': 'top', 'bottom': 'bottom', 'width': width}
            seg_map = {'x0': 'x0', 'x1': 'x1', 'y0': 'y0', 'y1': 'y1'}
            whisk_map = {'x': 'index', 'y': vdim, 'width': 0.2, 'height': 0.001}
            out_map = {'x': 'index', 'y': vdim}
        vbar2_map = dict(vbar_map)

        # Get color values
        if self.color_index is not None:
            cdim = element.get_dimension(self.color_index)
            cidx = element.get_dimension_index(self.color_index)
        else:
            cdim, cidx = None, None

        factors = []
        for key, g in groups.items():
            # Compute group label
            if element.kdims:
                label = tuple(d.pprint_value(v) for d, v in zip(element.kdims, key))
                if len(label) == 1:
                    label = label[0]
            else:
                label = key
            hover = any(isinstance(t, HoverTool) for t in self.state.tools)

            # Add color factor
            if cidx is not None and cidx<element.ndims:
                factors.append(cdim.pprint_value(wrap_tuple(key)[cidx]))
            else:
                factors.append(label)

            # Compute statistics
            vals = g.dimension_values(g.vdims[0])
            vals = vals[np.isfinite(vals)]
            if len(vals):
                q1, q2, q3 = (np.percentile(vals, q=q)
                              for q in range(25, 100, 25))
                iqr = q3 - q1
                upper = min(q3 + 1.5*iqr, vals.max())
                lower = max(q1 - 1.5*iqr, vals.min())
            else:
                q1, q2, q3 = 0, 0, 0
                lower, upper = 0, 0
            outliers = vals[(vals>upper) | (vals<lower)]
            # Add to CDS data
            for data in [r1_data, r2_data, w1_data, w2_data]:
                data['index'].append(label)
            for data in [s1_data, s2_data]:
                data['x0'].append(label)
                data['x1'].append(label)
            r1_data['top'].append(q2)
            r2_data['top'].append(q1)
            r1_data['bottom'].append(q3)
            r2_data['bottom'].append(q2)
            s1_data['y0'].append(upper)
            s2_data['y0'].append(lower)
            s1_data['y1'].append(q3)
            s2_data['y1'].append(q1)
            w1_data[vdim].append(lower)
            w2_data[vdim].append(upper)
            if len(outliers):
                out_data['index'] += [label]*len(outliers)
                out_data[vdim] += list(outliers)
                if hover:
                    for kd, k in zip(element.kdims, wrap_tuple(key)):
                        out_data[dimension_sanitizer(kd.name)] += [k]*len(outliers)
            if hover:
                for kd, k in zip(element.kdims, wrap_tuple(key)):
                    kd_name = dimension_sanitizer(kd.name)
                    if kd_name in r1_data:
                        r1_data[kd_name].append(k)
                    else:
                        r1_data[kd_name] = [k]
                    if kd_name in r2_data:
                        r2_data[kd_name].append(k)
                    else:
                        r2_data[kd_name] = [k]
                if vdim in r1_data:
                    r1_data[vdim].append(q2)
                else:
                    r1_data[vdim] = [q2]
                if vdim in r2_data:
                    r2_data[vdim].append(q2)
                else:
                    r2_data[vdim] = [q2]

        # Define combined data and mappings
        bar_glyph = 'hbar' if self.invert_axes else 'vbar'
        data = {
            bar_glyph+'_1': r1_data, bar_glyph+'_2': r2_data, 'segment_1': s1_data,
            'segment_2': s2_data, 'rect_1': w1_data, 'rect_2': w2_data,
            'circle_1': out_data
        }
        mapping = {
            bar_glyph+'_1': vbar_map, bar_glyph+'_2': vbar2_map, 'segment_1': seg_map,
            'segment_2': seg_map, 'rect_1': whisk_map, 'rect_2': whisk_map,
            'circle_1': out_map
        }

        # Cast data to arrays to take advantage of base64 encoding
        for gdata in [r1_data, r2_data, s1_data, s2_data, w1_data, w2_data, out_data]:
            for k, values in gdata.items():
                gdata[k] = np.array(values)

        # Return if not grouped
        if not element.kdims:
            return data, mapping, style

        # Define color dimension and data
        if cidx is None or cidx>=element.ndims:
            cdim = Dimension('index')
        else:
            r1_data[dimension_sanitizer(cdim.name)] = factors
            r2_data[dimension_sanitizer(cdim.name)] = factors
            factors = list(unique_iterator(factors))

        # Get colors and define categorical colormapper
        cname = dimension_sanitizer(cdim.name)
        cmap = style.get('cmap')
        if cmap is None:
            cycle_style = self.lookup_options(element, 'style')
            styles = cycle_style.max_cycles(len(factors))
            colors = [styles[i].get('box_color', styles[i]['box_fill_color'])
                      for i in range(len(factors))]
            colors = [rgb2hex(c) if isinstance(c, tuple) else c for c in colors]
        else:
            colors = None
        mapper = self._get_colormapper(cdim, element, ranges, style, factors, colors)
        vbar_map['fill_color'] = {'field': cname, 'transform': mapper}
        vbar2_map['fill_color'] = {'field': cname, 'transform': mapper}
        if self.show_legend:
            vbar_map['legend'] = cdim.name

        return data, mapping, style