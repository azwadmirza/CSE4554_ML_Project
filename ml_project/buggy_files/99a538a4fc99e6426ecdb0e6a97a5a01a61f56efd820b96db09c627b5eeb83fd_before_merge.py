    def glyph(dataset, orient=True, scale=True, factor=1.0, geom=None,
              subset=None):
        """
        Copies a geometric representation (called a glyph) to every
        point in the input dataset.  The glyph may be oriented along
        the input vectors, and it may be scaled according to scalar
        data or vector magnitude.

        Parameters
        ----------
        orient : bool
            Use the active vectors array to orient the the glyphs

        scale : bool
            Use the active scalars to scale the glyphs

        factor : float
            Scale factor applied to sclaing array

        geom : vtk.vtkDataSet
            The geometry to use for the glyph

        subset : float, optional
            Take a percentage subset of the mesh's points. Float value is
            percent subset between 0 and 1.
        """
        if subset is not None:
            if subset <= 0.0 or subset > 1.0:
                raise RuntimeError('subset must be a percentage between 0 and 1.')
            ids = np.random.randint(low=0, high=dataset.n_points-1,
                                    size=int(dataset.n_points * subset))
            small = pyvista.PolyData(dataset.points[ids])
            for name in dataset.point_arrays.keys():
                small.point_arrays[name] = dataset.point_arrays[name][ids]
            dataset = small
        if geom is None:
            arrow = vtk.vtkArrowSource()
            arrow.Update()
            geom = arrow.GetOutput()
        alg = vtk.vtkGlyph3D()
        alg.SetSourceData(geom)
        if isinstance(scale, str):
            dataset.active_scalar_name = scale
            scale = True
        if scale:
            if dataset.active_scalar is not None:
                if dataset.active_scalar.ndim > 1:
                    alg.SetScaleModeToScaleByVector()
                else:
                    alg.SetScaleModeToScaleByScalar()
        else:
            alg.SetScaleModeToDataScalingOff()
        if isinstance(orient, str):
            dataset.active_vectors_name = orient
            orient = True
        alg.SetOrient(orient)
        alg.SetInputData(dataset)
        alg.SetVectorModeToUseVector()
        alg.SetScaleFactor(factor)
        alg.Update()
        return _get_output(alg)