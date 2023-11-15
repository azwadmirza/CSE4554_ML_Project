    def glyph(dataset, orient=True, scale=True, factor=1.0, geom=None,
              tolerance=0.0, absolute=False):
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

        tolerance : float, optional
            Specify tolerance in terms of fraction of bounding box length.
            Float value is between 0 and 1. Default is 0.0. If ``absolute``
            is ``True`` then the tolerance can be an absolute distance.

        absolute : bool, optional
            Control if ``tolerance`` is an absolute distance or a fraction.
        """
        # Clean the points before glyphing
        small = pyvista.PolyData(dataset.points)
        small.point_arrays.update(dataset.point_arrays)
        dataset = small.clean(point_merging=True, merge_tol=tolerance,
                              lines_to_points=False, polys_to_lines=False,
                              strips_to_polys=False, inplace=False,
                              absolute=absolute)
        # Make glyphing geometry
        if geom is None:
            arrow = vtk.vtkArrowSource()
            arrow.Update()
            geom = arrow.GetOutput()
        # Run the algorithm
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