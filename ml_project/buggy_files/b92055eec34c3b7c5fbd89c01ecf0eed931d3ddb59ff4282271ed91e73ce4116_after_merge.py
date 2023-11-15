    def add_legend_data(self, ax):
        """Add labeled artists to represent the different plot semantics."""
        verbosity = self.legend
        if verbosity not in ["brief", "full"]:
            err = "`legend` must be 'brief', 'full', or False"
            raise ValueError(err)

        legend_kwargs = {}
        keys = []

        title_kws = dict(color="w", s=0, linewidth=0, marker="", dashes="")

        def update(var_name, val_name, **kws):

            key = var_name, val_name
            if key in legend_kwargs:
                legend_kwargs[key].update(**kws)
            else:
                keys.append(key)

                legend_kwargs[key] = dict(**kws)

        # -- Add a legend for hue semantics
        if verbosity == "brief" and self._hue_map.map_type == "numeric":
            if isinstance(self._hue_map.norm, mpl.colors.LogNorm):
                locator = mpl.ticker.LogLocator(numticks=3)
            else:
                locator = mpl.ticker.MaxNLocator(nbins=3)
            limits = min(self._hue_map.levels), max(self._hue_map.levels)
            hue_levels, hue_formatted_levels = locator_to_legend_entries(
                locator, limits, self.plot_data["hue"].infer_objects().dtype
            )
        elif self._hue_map.levels is None:
            hue_levels = hue_formatted_levels = []
        else:
            hue_levels = hue_formatted_levels = self._hue_map.levels

        # Add the hue semantic subtitle
        if "hue" in self.variables and self.variables["hue"] is not None:
            update((self.variables["hue"], "title"),
                   self.variables["hue"], **title_kws)

        # Add the hue semantic labels
        for level, formatted_level in zip(hue_levels, hue_formatted_levels):
            if level is not None:
                color = self._hue_map(level)
                update(self.variables["hue"], formatted_level, color=color)

        # -- Add a legend for size semantics

        if verbosity == "brief" and self._size_map.map_type == "numeric":
            # Define how ticks will interpolate between the min/max data values
            if isinstance(self._size_map.norm, mpl.colors.LogNorm):
                locator = mpl.ticker.LogLocator(numticks=3)
            else:
                locator = mpl.ticker.MaxNLocator(nbins=3)
            # Define the min/max data values
            limits = min(self._size_map.levels), max(self._size_map.levels)
            size_levels, size_formatted_levels = locator_to_legend_entries(
                locator, limits, self.plot_data["size"].infer_objects().dtype
            )
        elif self._size_map.levels is None:
            size_levels = size_formatted_levels = []
        else:
            size_levels = size_formatted_levels = self._size_map.levels

        # Add the size semantic subtitle
        if "size" in self.variables and self.variables["size"] is not None:
            update((self.variables["size"], "title"),
                   self.variables["size"], **title_kws)

        # Add the size semantic labels
        for level, formatted_level in zip(size_levels, size_formatted_levels):
            if level is not None:
                size = self._size_map(level)
                update(
                    self.variables["size"],
                    formatted_level,
                    linewidth=size,
                    s=size,
                )

        # -- Add a legend for style semantics

        # Add the style semantic title
        if "style" in self.variables and self.variables["style"] is not None:
            update((self.variables["style"], "title"),
                   self.variables["style"], **title_kws)

        # Add the style semantic labels
        if self._style_map.levels is not None:
            for level in self._style_map.levels:
                if level is not None:
                    attrs = self._style_map(level)
                    update(
                        self.variables["style"],
                        level,
                        marker=attrs.get("marker", ""),
                        dashes=attrs.get("dashes", ""),
                    )

        func = getattr(ax, self._legend_func)

        legend_data = {}
        legend_order = []

        for key in keys:

            _, label = key
            kws = legend_kwargs[key]
            kws.setdefault("color", ".2")
            use_kws = {}
            for attr in self._legend_attributes + ["visible"]:
                if attr in kws:
                    use_kws[attr] = kws[attr]
            artist = func([], [], label=label, **use_kws)
            if self._legend_func == "plot":
                artist = artist[0]
            legend_data[key] = artist
            legend_order.append(key)

        self.legend_data = legend_data
        self.legend_order = legend_order