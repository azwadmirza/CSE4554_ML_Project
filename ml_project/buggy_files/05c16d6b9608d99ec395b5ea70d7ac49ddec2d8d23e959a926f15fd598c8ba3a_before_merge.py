    def plot(self, axes=None, resample=None, annotate=True,
             interval=200, plot_function=None, **kwargs):
        """
        A animation plotting routine that animates each element in the
        MapCube

        Parameters
        ----------
        gamma: float
            Gamma value to use for the color map

        axes: mpl axes
            axes to plot the animation on, if none uses current axes

        resample: list or False
            Draws the map at a lower resolution to increase the speed of
            animation. Specify a list as a fraction i.e. [0.25, 0.25] to
            plot at 1/4 resolution.
            [Note: this will only work where the map arrays are the same size]

        annotate: bool
            Annotate the figure with scale and titles

        interval: int
            Animation interval in ms

        plot_function : function
            A function to be called as each map is plotted. Any variables
            returned from the function will have their ``remove()`` method called
            at the start of the next frame so that they are removed from the plot.

        Examples
        --------
        >>> import matplotlib.pyplot as plt
        >>> import matplotlib.animation as animation
        >>> from sunpy.map import Map

        >>> cube = Map(files, cube=True)   # doctest: +SKIP
        >>> ani = cube.plot(colorbar=True)   # doctest: +SKIP
        >>> plt.show()   # doctest: +SKIP

        Plot the map at 1/2 original resolution

        >>> cube = Map(files, cube=True)   # doctest: +SKIP
        >>> ani = cube.plot(resample=[0.5, 0.5], colorbar=True)   # doctest: +SKIP
        >>> plt.show()   # doctest: +SKIP

        Save an animation of the MapCube

        >>> cube = Map(res, cube=True)   # doctest: +SKIP

        >>> ani = cube.plot()   # doctest: +SKIP

        >>> Writer = animation.writers['ffmpeg']   # doctest: +SKIP
        >>> writer = Writer(fps=10, metadata=dict(artist='SunPy'), bitrate=1800)   # doctest: +SKIP

        >>> ani.save('mapcube_animation.mp4', writer=writer)   # doctest: +SKIP

        Save an animation with the limb at each time step

        >>> def myplot(fig, ax, sunpy_map):
        ...    p = sunpy_map.draw_limb()
        ...    return p
        >>> cube = Map(files, cube=True)   # doctest: +SKIP
        >>> ani = cube.peek(plot_function=myplot)   # doctest: +SKIP
        >>> plt.show()   # doctest: +SKIP

        """
        if not axes:
            axes = wcsaxes_compat.gca_wcs(self.maps[0].wcs)
        fig = axes.get_figure()

        if not plot_function:
            plot_function = lambda fig, ax, smap: []
        removes = []

        # Normal plot
        def annotate_frame(i):
            axes.set_title("{s.name}".format(s=self[i]))

            # x-axis label
            if self[0].coordinate_system.x == 'HG':
                xlabel = 'Longitude [{lon}'.format(lon=self[i].spatial_units.x)
            else:
                xlabel = 'X-position [{xpos}]'.format(xpos=self[i].spatial_units.x)

            # y-axis label
            if self[0].coordinate_system.y == 'HG':
                ylabel = 'Latitude [{lat}]'.format(lat=self[i].spatial_units.y)
            else:
                ylabel = 'Y-position [{ypos}]'.format(ypos=self[i].spatial_units.y)

            axes.set_xlabel(xlabel)
            axes.set_ylabel(ylabel)

        if resample:
            if self.all_maps_same_shape():
                resample = u.Quantity(self.maps[0].dimensions) * np.array(resample)
                ani_data = [amap.resample(resample) for amap in self.maps]
            else:
                raise ValueError('Maps in mapcube do not all have the same shape.')
        else:
            ani_data = self.maps

        im = ani_data[0].plot(axes=axes, **kwargs)

        def updatefig(i, im, annotate, ani_data, removes):
            while removes:
                removes.pop(0).remove()

            im.set_array(ani_data[i].data)
            im.set_cmap(ani_data[i].plot_settings['cmap'])

            norm = deepcopy(ani_data[i].plot_settings['norm'])
            # The following explicit call is for bugged versions of Astropy's
            # ImageNormalize
            norm.autoscale_None(ani_data[i].data)
            im.set_norm(norm)

            if wcsaxes_compat.is_wcsaxes(axes):
                im.axes.reset_wcs(ani_data[i].wcs)
                wcsaxes_compat.default_wcs_grid(axes)
            else:
                im.set_extent(np.concatenate((ani_data[i].xrange.value,
                                              ani_data[i].yrange.value)))

            if annotate:
                annotate_frame(i)
            removes += list(plot_function(fig, axes, ani_data[i]))

        ani = matplotlib.animation.FuncAnimation(fig, updatefig,
                                                 frames=list(range(0, len(ani_data))),
                                                 fargs=[im, annotate, ani_data, removes],
                                                 interval=interval,
                                                 blit=False)

        return ani