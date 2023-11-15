    def add_volume(self, volume, scalars=None, resolution=None,
                   opacity='linear', n_colors=256, cmap=None, flip_scalars=False,
                   reset_camera=None, name=None, ambient=0.0, categories=False,
                   loc=None, backface_culling=False, multi_colors=False,
                   blending='additive', mapper='fixed_point', rng=None,
                   stitle=None, scalar_bar_args=None,
                   show_scalar_bar=None, **kwargs):
        """
        Adds a volume, rendered using a fixed point ray cast mapper by default.

        Requires a 3D numpy.ndarray or pyvista.UniformGrid.

        Parameters
        ----------
        data: 3D numpy.ndarray or pyvista.UnformGrid
            The input array to visualize, assuming the array values denote
            scalar intensities.

        opacity : float or string, optional
            Opacity of input array. Options are: linear, linear_r, geom, geom_r.
            Defaults to 'linear'. Can also be given as a scalar value between 0
            and 1.

        flip_scalars : bool, optional
            Flip direction of cmap.

        n_colors : int, optional
            Number of colors to use when displaying scalars.  Default
            256.

        cmap : str, optional
           cmap string.  See available matplotlib cmaps. Only applicable for when
           displaying scalars.  Defaults to None (jet).  Requires matplotlib.
           Will be overridden if multi_colors is set to True.

        name : str, optional
            The name for the added actor so that it can be easily
            updated.  If an actor of this name already exists in the
            rendering window, it will be replaced by the new actor.

        ambient : float, optional
            The amount of light from 0 to 1 that reaches the actor when not
            directed at the light source emitted from the viewer.  Default 0.0.

        loc : int, tuple, or list
            Index of the renderer to add the actor to.  For example,
            ``loc=2`` or ``loc=(1, 1)``.  If None, selects the last
            active Renderer.

        backface_culling : bool optional
            Does not render faces that should not be visible to the
            plotter.  This can be helpful for dense surface meshes,
            especially when edges are visible, but can cause flat
            meshes to be partially displayed.  Default False.

        categories : bool, optional
            If fetching a colormap from matplotlib, this is the number of
            categories to use in that colormap. If set to ``True``, then
            the number of unique values in the scalar array will be used.

        multi_colors : bool, optional
            Whether or not to use multiple colors when plotting MultiBlock
            object. Blocks will be colored sequentially as 'Reds', 'Greens',
            'Blues', and 'Grays'.

        blending : str, optional
            Blending mode for visualisation of the input object(s). Can be
            one of 'additive', 'maximum', 'minimum', 'composite', or
            'average'. Defaults to 'additive'.

        Returns
        -------
        actor: vtk.vtkVolume
            VTK volume of the input data.
        """

        # Handle default arguments

        if name is None:
            name = '{}({})'.format(type(volume).__name__, str(hex(id(volume))))

        if rng is None:
            rng = kwargs.get('clim', None)

        if scalar_bar_args is None:
            scalar_bar_args = {}

        if show_scalar_bar is None:
            show_scalar_bar = rcParams['show_scalar_bar']

        # Convert the VTK data object to a pyvista wrapped object if neccessary
        if not is_pyvista_obj(volume):
            if isinstance(volume, np.ndarray):
                volume = wrap(volume)
                if resolution is None:
                    resolution = [1,1,1]
                elif len(resolution) != 3:
                    raise ValueError('Invalid resolution dimensions.')
                volume.spacing = resolution
            else:
                volume = wrap(volume)
        else:
            # HACK: Make a copy so the original object is not altered
            volume = volume.copy()


        if isinstance(volume, pyvista.MultiBlock):
            from itertools import cycle
            cycler = cycle(['Reds', 'Greens', 'Blues', 'Greys', 'Oranges', 'Purples'])
            # Now iteratively plot each element of the multiblock dataset
            actors = []
            for idx in range(volume.GetNumberOfBlocks()):
                if volume[idx] is None:
                    continue
                # Get a good name to use
                next_name = '{}-{}'.format(name, idx)
                # Get the data object
                block = wrap(volume.GetBlock(idx))
                if resolution is None:
                    try:
                        block_resolution = block.GetSpacing()
                    except:
                        block_resolution = resolution
                else:
                    block_resolution = resolution
                if multi_colors:
                    color = next(cycler)
                else:
                    color = cmap

                a = self.add_volume(block, resolution=block_resolution, opacity=opacity,
                                    n_colors=n_colors, cmap=color, flip_scalars=flip_scalars,
                                    reset_camera=reset_camera, name=next_name,
                                    ambient=ambient, categories=categories, loc=loc,
                                    backface_culling=backface_culling, rng=rng,
                                    mapper=mapper, **kwargs)

                actors.append(a)
            return actors

        if not isinstance(volume, pyvista.UniformGrid):
            raise TypeError('Type ({}) not supported for volume rendering at this time. Use `pyvista.UniformGrid`.')


        if scalars is None:
            # Make sure scalar components are not vectors/tuples
            scalars = volume.active_scalar
            # Don't allow plotting of string arrays by default
            if scalars is not None and np.issubdtype(scalars.dtype, np.number):
                if stitle is None:
                    stitle = volume.active_scalar_info[1]
            else:
                raise RuntimeError('No scalars to use for volume rendering.')
        elif isinstance(scalars, str):
            pass

        ##############

        title = 'Data' if stitle is None else stitle
        append_scalars = False
        if isinstance(scalars, str):
            title = scalars
            scalars = get_scalar(volume, scalars,
                    preference=kwargs.get('preference', 'point'), err=True)
            if stitle is None:
                stitle = title
        else:
            append_scalars = True

        if not isinstance(scalars, np.ndarray):
            scalars = np.asarray(scalars)

        if not np.issubdtype(scalars.dtype, np.number):
            raise TypeError('Non-numeric scalars are currently not supported for plotting.')


        if scalars.ndim != 1:
            scalars = scalars.ravel()

        if scalars.dtype == np.bool or scalars.dtype == np.uint8:
            scalars = scalars.astype(np.float)

        # Define mapper, volume, and add the correct properties
        mappers = {
            'fixed_point' : vtk.vtkFixedPointVolumeRayCastMapper,
            'gpu' : vtk.vtkGPUVolumeRayCastMapper,
            'open_gl' : vtk.vtkOpenGLGPUVolumeRayCastMapper,
            'smart' : vtk.vtkSmartVolumeMapper,
        }
        if not isinstance(mapper, str) or mapper not in mappers.keys():
            raise RuntimeError('Mapper ({}) unknown. Available volume mappers include: {}'.format(mapper, ', '.join(mappers.keys())))
        self.mapper = make_mapper(mappers[mapper])

        # Scalar interpolation approach
        if scalars.shape[0] == volume.n_points:
            volume._add_point_scalar(scalars, title, append_scalars)
            self.mapper.SetScalarModeToUsePointData()
        elif scalars.shape[0] == volume.n_cells:
            volume._add_cell_scalar(scalars, title, append_scalars)
            self.mapper.SetScalarModeToUseCellData()
        else:
            raise_not_matching(scalars, volume)

        # Set scalar range
        if rng is None:
            rng = [np.nanmin(scalars), np.nanmax(scalars)]
        elif isinstance(rng, float) or isinstance(rng, int):
            rng = [-rng, rng]

        ###############

        scalars = scalars.astype(np.float)
        idxs0 = scalars < rng[0]
        idxs1 = scalars > rng[1]
        scalars[idxs0] = np.nan
        scalars[idxs1] = np.nan
        scalars = ((scalars - np.nanmin(scalars)) / (np.nanmax(scalars) - np.nanmin(scalars))) * 255
        # scalars = scalars.astype(np.uint8)
        volume[title] = scalars

        self.mapper.scalar_range = rng

        # Set colormap and build lookup table
        table = vtk.vtkLookupTable()
        # table.SetNanColor(nan_color) # NaN's are chopped out with current implementation
        if cmap is None: # grab alias for cmaps: colormap
            cmap = kwargs.get('colormap', None)
            if cmap is None: # Set default map if matplotlib is avaialble
                try:
                    import matplotlib
                    cmap = rcParams['cmap']
                except ImportError:
                    pass
        if cmap is not None:
            try:
                from matplotlib.cm import get_cmap
            except ImportError:
                cmap = None
                raise RuntimeError('Please install matplotlib for volume rendering.')
        if cmap is not None:
            cmap = get_cmap_safe(cmap)
            if categories:
                if categories is True:
                    n_colors = len(np.unique(scalars))
                elif isinstance(categories, int):
                    n_colors = categories
        if flip_scalars:
            cmap = cmap.reversed()


        color_tf = vtk.vtkColorTransferFunction()
        for ii in range(n_colors):
            color_tf.AddRGBPoint(ii, *cmap(ii)[:-1])

        # Set opacities
        if isinstance(opacity, (float, int)):
            opacity_values = [opacity] * n_colors
        elif isinstance(opacity, str):
            opacity_values = pyvista.opacity_transfer_function(opacity, n_colors)

        opacity_tf = vtk.vtkPiecewiseFunction()
        for ii in range(n_colors):
            opacity_tf.AddPoint(ii, opacity_values[ii] / n_colors)


        # Now put color tf and opacity tf into a lookup table for the scalar bar
        table.SetNumberOfTableValues(n_colors)
        lut = cmap(np.array(range(n_colors))) * 255
        lut[:,3] = opacity_values
        lut = lut.astype(np.uint8)
        table.SetTable(VN.numpy_to_vtk(lut))
        table.SetRange(*rng)
        self.mapper.lookup_table = table

        self.mapper.SetInputData(volume)

        blending = blending.lower()
        if blending in ['additive', 'add', 'sum']:
            self.mapper.SetBlendModeToAdditive()
        elif blending in ['average', 'avg', 'average_intensity']:
            self.mapper.SetBlendModeToAverageIntensity()
        elif blending in ['composite', 'comp']:
            self.mapper.SetBlendModeToComposite()
        elif blending in ['maximum', 'max', 'maximum_intensity']:
            self.mapper.SetBlendModeToMaximumIntensity()
        elif blending in ['minimum', 'min', 'minimum_intensity']:
            self.mapper.SetBlendModeToMinimumIntensity()
        else:
            raise ValueError('Blending mode \'{}\' invalid. '.format(blending) +
                             'Please choose one ' + 'of \'additive\', ' +
                             '\'composite\', \'minimum\' or ' + '\'maximum\'.')
        self.mapper.Update()

        self.volume = vtk.vtkVolume()
        self.volume.SetMapper(self.mapper)

        prop = vtk.vtkVolumeProperty()
        prop.SetColor(color_tf)
        prop.SetScalarOpacity(opacity_tf)
        prop.SetAmbient(ambient)
        self.volume.SetProperty(prop)

        actor, prop = self.add_actor(self.volume, reset_camera=reset_camera,
                                     name=name, loc=loc, culling=backface_culling)


        # Add scalar bar
        if stitle is not None and show_scalar_bar:
            self.add_scalar_bar(stitle, **scalar_bar_args)


        return actor