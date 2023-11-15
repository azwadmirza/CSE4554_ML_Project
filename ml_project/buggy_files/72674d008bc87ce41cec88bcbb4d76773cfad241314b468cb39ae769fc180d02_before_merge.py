    def clean(self, point_merging=True, merge_tol=None, lines_to_points=True,
              polys_to_lines=True, strips_to_polys=True, inplace=False):
        """
        Cleans mesh by merging duplicate points, remove unused
        points, and/or remove degenerate cells.

        Parameters
        ----------
        point_merging : bool, optional
            Enables point merging.  On by default.

        merge_tol : float, optional
            Set merging tolarance.  When enabled merging is set to
            absolute distance

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

        Returns
        -------
        mesh : pyvista.PolyData
            Cleaned mesh.  None when inplace=True
        """
        clean = vtk.vtkCleanPolyData()
        clean.SetConvertLinesToPoints(lines_to_points)
        clean.SetConvertPolysToLines(polys_to_lines)
        clean.SetConvertStripsToPolys(strips_to_polys)
        if merge_tol:
            clean.ToleranceIsAbsoluteOn()
            clean.SetAbsoluteTolerance(merge_tol)
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