    def clean(self, point_merging=True, merge_tol=None, lines_to_points=True,
              polys_to_lines=True, strips_to_polys=True, inplace=False,
              absolute=True, **kwargs):
        """
        Cleans mesh by merging duplicate points, remove unused
        points, and/or remove degenerate cells.

        Parameters
        ----------
        point_merging : bool, optional
            Enables point merging.  On by default.

        merge_tol : float, optional
            Set merging tolarance.  When enabled merging is set to
            absolute distance. If ``absolute`` is False, then the merging
            tolerance is a fraction of the bounding box legnth. The alias
            ``tolerance`` is also excepted.

        lines_to_points : bool, optional
            Turn on/off conversion of degenerate lines to points.  Enabled by
            default.

        polys_to_lines : bool, optional
            Turn on/off conversion of degenerate polys to lines.  Enabled by
            default.

        strips_to_polys : bool, optional
            Turn on/off conversion of degenerate strips to polys.

        inplace : bool, optional
            Updates mesh in-place while returning nothing.  Default True.

        absolute : bool, optional
            Control if ``merge_tol`` is an absolute distance or a fraction.

        Returns
        -------
        mesh : pyvista.PolyData
            Cleaned mesh.  None when inplace=True
        """
        if merge_tol is None:
            merge_tol = kwargs.pop('tolerance', None)
        clean = vtk.vtkCleanPolyData()
        clean.SetConvertLinesToPoints(lines_to_points)
        clean.SetConvertPolysToLines(polys_to_lines)
        clean.SetConvertStripsToPolys(strips_to_polys)
        if isinstance(merge_tol, (int, float)):
            if absolute:
                clean.ToleranceIsAbsoluteOn()
                clean.SetAbsoluteTolerance(merge_tol)
            else:
                clean.SetTolerance(merge_tol)
        clean.SetInputData(self)
        clean.Update()

        output = _get_output(clean)

        # Check output so no segfaults occur
        if output.n_points < 1:
            raise AssertionError('Clean tolerance is too high. Empty mesh returned.')

        if inplace:
            self.overwrite(output)
        else:
            return output