    def add_mesh(self, mesh, color=None, style=None,
                 scalars=None, rng=None, stitle=None, showedges=True,
                 psize=5.0, opacity=1, linethick=None, flipscalars=False,
                 lighting=False, ncolors=256, interpolatebeforemap=False,
                 colormap=None, label=None, **kwargs):
        """
        Adds a unstructured, structured, or surface mesh to the plotting object.

        Also accepts a 3D numpy.ndarray

        Parameters
        ----------
        mesh : vtk unstructured, structured, polymesh, or 3D numpy.ndarray
            A vtk unstructured, structured, or polymesh to plot.

        color : string or 3 item list, optional, defaults to white
            Either a string, rgb list, or hex color string.  For example:
                color='white'
                color='w'
                color=[1, 1, 1]
                color='#FFFFFF'

            Color will be overridden when scalars are input.

        style : string, optional
            Visualization style of the vtk mesh.  One for the following:
                style='surface'
                style='wireframe'
                style='points'

            Defaults to 'surface'

        scalars : numpy array, optional
            Scalars used to "color" the mesh.  Accepts an array equal to the
            number of cells or the number of points in the mesh.  Array should
            be sized as a single vector.

        rng : 2 item list, optional
            Range of mapper for scalars.  Defaults to minimum and maximum of
            scalars array.  Example: [-1, 2]

        stitle : string, optional
            Scalar title.  By default there is no scalar legend bar.  Setting
            this creates the legend bar and adds a title to it.  To create a
            bar with no title, use an empty string (i.e. '').

        showedges : bool, optional
            Shows the edges of a mesh.  Does not apply to a wireframe
            representation.

        psize : float, optional
            Point size.  Applicable when style='points'.  Default 5.0

        opacity : float, optional
            Opacity of mesh.  Should be between 0 and 1.  Default 1.0

        linethick : float, optional
            Thickness of lines.  Only valid for wireframe and surface
            representations.  Default None.

        flipscalars : bool, optional
            Flip direction of colormap.

        lighting : bool, optional
            Enable or disable view direction lighting.  Default False.

        ncolors : int, optional
            Number of colors to use when displaying scalars.  Default 256.

        interpolatebeforemap : bool, optional
            Enabling makes for a smoother scalar display.  Default False

        colormap : str, optional
           Colormap string.  See available matplotlib colormaps.  Only applicable for
           when displaying scalars.  Defaults None (rainbow).  Requires matplotlib.

        Returns
        -------
        actor: vtk.vtkActor
            VTK actor of the mesh.
        """
        if isinstance(mesh, np.ndarray):
            mesh = vtki.PolyData(mesh)
            style = 'points'

        try:
            if mesh._is_vtki:
                pass
        except:
            # Convert the VTK data object to a vtki wrapped object
            mesh = wrap(mesh)

        # set main values
        self.mesh = mesh
        self.mapper = vtk.vtkDataSetMapper()
        self.mapper.SetInputData(self.mesh)
        actor, prop = self.add_actor(self.mapper)
        self._update_bounds(mesh.GetBounds())

        # Scalar formatting ===================================================
        if scalars is not None:
            # if scalars is a string, then get the first array found with that name
            if isinstance(scalars, str):
                tit = scalars
                scalars = get_scalar(mesh, scalars)
                if stitle is None:
                    stitle = tit

            if not isinstance(scalars, np.ndarray):
                scalars = np.asarray(scalars)

            if scalars.ndim != 1:
                scalars = scalars.ravel()

            if scalars.dtype == np.bool:
                scalars = scalars.astype(np.float)

            # Scalar interpolation approach
            if scalars.size == mesh.GetNumberOfPoints():
                self.mesh._add_point_scalar(scalars, '', True)
                self.mapper.SetScalarModeToUsePointData()
                self.mapper.GetLookupTable().SetNumberOfTableValues(ncolors)
                if interpolatebeforemap:
                    self.mapper.InterpolateScalarsBeforeMappingOn()
            elif scalars.size == mesh.GetNumberOfCells():
                self.mesh._add_cell_scalar(scalars, '', True)
                self.mapper.SetScalarModeToUseCellData()
                self.mapper.GetLookupTable().SetNumberOfTableValues(ncolors)
            else:
                _raise_not_matching(scalars, mesh)

            # Set scalar range
            if not rng:
                rng = [np.nanmin(scalars), np.nanmax(scalars)]
            elif isinstance(rng, float) or isinstance(rng, int):
                rng = [-rng, rng]

            if np.any(rng):
                self.mapper.SetScalarRange(rng[0], rng[1])

            # Flip if requested
            table = self.mapper.GetLookupTable()
            if colormap is not None:
                try:
                    from matplotlib.cm import get_cmap
                except ImportError:
                    raise Exception('colormap requires matplotlib')
                cmap = get_cmap(colormap)
                ctable = cmap(np.linspace(0, 1, ncolors))*255
                ctable = ctable.astype(np.uint8)
                if flipscalars:
                    ctable = np.ascontiguousarray(ctable[::-1])
                table.SetTable(VN.numpy_to_vtk(ctable))

            else:  # no colormap specified
                if flipscalars:
                    self.mapper.GetLookupTable().SetHueRange(0.0, 0.66667)
                else:
                    self.mapper.GetLookupTable().SetHueRange(0.66667, 0.0)

        else:
            self.mapper.SetScalarModeToUseFieldData()

        # select view style
        if not style:
            style = 'surface'
        style = style.lower()
        if style == 'wireframe':
            prop.SetRepresentationToWireframe()
        elif style == 'points':
            prop.SetRepresentationToPoints()
        elif style == 'surface':
            prop.SetRepresentationToSurface()
        else:
            raise Exception('Invalid style.  Must be one of the following:\n' +
                            '\t"surface"\n' +
                            '\t"wireframe"\n' +
                            '\t"points"\n')

        prop.SetPointSize(psize)

        # edge display style
        if showedges:
            prop.EdgeVisibilityOn()

        rgb_color = parse_color(color)
        prop.SetColor(rgb_color)
        prop.SetOpacity(opacity)

        # legend label
        if label:
            assert isinstance(label, str), 'Label must be a string'
            self._labels.append([single_triangle(), label, rgb_color])

        # lighting display style
        if lighting is False:
            prop.LightingOff()

        # set line thickness
        if linethick:
            prop.SetLineWidth(linethick)

        # Add scalar bar if available
        if stitle is not None:
            self.add_scalar_bar(stitle)

        return actor