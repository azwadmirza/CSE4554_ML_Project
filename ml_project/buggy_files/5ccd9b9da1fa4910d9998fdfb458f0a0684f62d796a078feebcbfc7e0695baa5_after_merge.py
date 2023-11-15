    def __call__(self, plot):
        from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

        # Callback only works for plots with axis ratios of 1
        xsize = plot.xlim[1] - plot.xlim[0]

        # Setting pos overrides corner argument
        if self.pos is None:
            if self.corner == 'upper_left':
                self.pos = (0.11, 0.952)
            elif self.corner == 'upper_right':
                self.pos = (0.89, 0.952)
            elif self.corner == 'lower_left':
                self.pos = (0.11, 0.052)
            elif self.corner == 'lower_right':
                self.pos = (0.89, 0.052)
            elif self.corner is None:
                self.pos = (0.5, 0.5)
            else:
                raise SyntaxError("Argument 'corner' must be set to "
                                  "'upper_left', 'upper_right', 'lower_left', "
                                  "'lower_right', or None")

        # When identifying a best fit distance unit, do not allow scale marker
        # to be greater than max_frac fraction of xaxis or under min_frac
        # fraction of xaxis
        max_scale = self.max_frac * xsize
        min_scale = self.min_frac * xsize

        if self.coeff is None:
            self.coeff = 1.

        # If no units are set, then identify a best fit distance unit
        if self.unit is None:
            min_scale = plot.ds.get_smallest_appropriate_unit(
                min_scale, return_quantity=True)
            max_scale = plot.ds.get_smallest_appropriate_unit(
                max_scale, return_quantity=True)
            self.coeff = max_scale.v
            self.unit = max_scale.units
        self.scale = YTQuantity(self.coeff, self.unit)
        text = "{scale} {units}".format(scale=int(self.coeff), units=self.unit)
        image_scale = (plot.frb.convert_distance_x(self.scale) /
                       plot.frb.convert_distance_x(xsize)).v
        size_vertical = self.size_bar_args.pop(
            'size_vertical', .005 * plot.aspect)
        fontproperties = self.size_bar_args.pop(
            'fontproperties', plot.font_properties.copy())
        frameon = self.size_bar_args.pop('frameon', self.draw_inset_box)
        # FontProperties instances use set_<property>() setter functions
        for key, val in self.text_args.items():
            setter_func = "set_"+key
            try:
                getattr(fontproperties, setter_func)(val)
            except AttributeError:
                raise AttributeError("Cannot set text_args keyword " \
                "to include '%s' because MPL's fontproperties object does " \
                "not contain function '%s'." % (key, setter_func))

        # this "anchors" the size bar to a box centered on self.pos in axis
        # coordinates
        self.size_bar_args['bbox_to_anchor'] = self.pos
        self.size_bar_args['bbox_transform'] = plot._axes.transAxes

        bar = AnchoredSizeBar(plot._axes.transAxes, image_scale, text, 10,
                              size_vertical=size_vertical,
                              fontproperties=fontproperties,
                              frameon=frameon,
                              **self.size_bar_args)

        bar.patch.set(**self.inset_box_args)

        plot._axes.add_artist(bar)

        return plot