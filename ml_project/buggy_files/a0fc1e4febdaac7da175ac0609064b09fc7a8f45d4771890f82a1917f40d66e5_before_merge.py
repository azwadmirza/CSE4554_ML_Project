    def _get_colormapper(self, eldim, element, ranges, style, factors=None, colors=None,
                         group=None, name='color_mapper'):
        # The initial colormapper instance is cached the first time
        # and then only updated
        if eldim is None and colors is None:
            return None
        dim_name = dim_range_key(eldim)

        # Attempt to find matching colormapper on the adjoined plot
        if self.adjoined:
            cmapper_name = dim_name+name
            cmappers = self.adjoined.traverse(lambda x: (x.handles.get('color_dim'),
                                                         x.handles.get(name, x.handles.get(cmapper_name))))
            cmappers = [cmap for cdim, cmap in cmappers if cdim == eldim]
            if cmappers:
                cmapper = cmappers[0]
                self.handles['color_mapper'] = cmapper
                return cmapper
            else:
                return None

        ncolors = None if factors is None else len(factors)
        if eldim:
            # check if there's an actual value (not np.nan)
            if all(util.isfinite(cl) for cl in self.clim):
                low, high = self.clim
            elif dim_name in ranges:
                low, high = ranges[dim_name]['combined']
                dlow, dhigh = ranges[dim_name]['data']
                if (util.is_int(low, int_like=True) and
                    util.is_int(high, int_like=True) and
                    util.is_int(dlow) and
                    util.is_int(dhigh)):
                    low, high = int(low), int(high)
            elif isinstance(eldim, dim):
                low, high = np.nan, np.nan
            else:
                low, high = element.range(eldim.name)
            if self.symmetric:
                sym_max = max(abs(low), high)
                low, high = -sym_max, sym_max
            low = self.clim[0] if util.isfinite(self.clim[0]) else low
            high = self.clim[1] if util.isfinite(self.clim[1]) else high
        else:
            low, high = None, None

        prefix = '' if group is None else group+'_'
        cmap = colors or style.get(prefix+'cmap', style.get('cmap', 'viridis'))
        nan_colors = {k: rgba_tuple(v) for k, v in self.clipping_colors.items()}
        if isinstance(cmap, dict):
            if factors is None:
                factors = list(cmap)
            palette = [cmap.get(f, nan_colors.get('NaN', self._default_nan)) for f in factors]
            if isinstance(eldim, dim):
                if eldim.dimension in element:
                    formatter = element.get_dimension(eldim.dimension).pprint_value
                else:
                    formatter = str
            else:
                formatter = eldim.pprint_value
            factors = [formatter(f) for f in factors]
        else:
            categorical = ncolors is not None
            if isinstance(self.color_levels, int):
                ncolors = self.color_levels
            elif isinstance(self.color_levels, list):
                ncolors = len(self.color_levels) - 1
                if isinstance(cmap, list) and len(cmap) != ncolors:
                    raise ValueError('The number of colors in the colormap '
                                     'must match the intervals defined in the '
                                     'color_levels, expected %d colors found %d.'
                                     % (ncolors, len(cmap)))
            palette = process_cmap(cmap, ncolors, categorical=categorical)
            if isinstance(self.color_levels, list):
                palette, (low, high) = color_intervals(palette, self.color_levels, clip=(low, high))
        colormapper, opts = self._get_cmapper_opts(low, high, factors, nan_colors)

        cmapper = self.handles.get(name)
        if cmapper is not None:
            if cmapper.palette != palette:
                cmapper.palette = palette
            opts = {k: opt for k, opt in opts.items()
                    if getattr(cmapper, k) != opt}
            if opts:
                cmapper.update(**opts)
        else:
            cmapper = colormapper(palette=palette, **opts)
            self.handles[name] = cmapper
            self.handles['color_dim'] = eldim
        return cmapper