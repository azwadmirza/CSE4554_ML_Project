    def __call__(self, x, y, dx=0, dy=0, grid=True):
        """
        Evaluate the spline or its derivatives at given positions.

        Parameters
        ----------
        x, y : array_like
            Input coordinates.

            If `grid` is False, evaluate the spline at points ``(x[i],
            y[i]), i=0, ..., len(x)-1``.  Standard Numpy broadcasting
            is obeyed.

            If `grid` is True: evaluate spline at the grid points
            defined by the coordinate arrays x, y. The arrays must be
            sorted to increasing order.
        dx : int
            Order of x-derivative

            .. versionadded:: 0.14.0
        dy : int
            Order of y-derivative

            .. versionadded:: 0.14.0
        grid : bool
            Whether to evaluate the results on a grid spanned by the
            input arrays, or at points specified by the input arrays.

            .. versionadded:: 0.14.0

        """
        x = np.asarray(x)
        y = np.asarray(y)

        tx, ty, c = self.tck[:3]
        kx, ky = self.degrees
        if grid:
            if x.size == 0 or y.size == 0:
                return np.zeros((x.size, y.size), dtype=self.tck[2].dtype)

            if dx or dy:
                z,ier = dfitpack.parder(tx,ty,c,kx,ky,dx,dy,x,y)
                if not ier == 0:
                    raise ValueError("Error code returned by parder: %s" % ier)
            else:
                z,ier = dfitpack.bispev(tx,ty,c,kx,ky,x,y)
                if not ier == 0:
                    raise ValueError("Error code returned by bispev: %s" % ier)
        else:
            # standard Numpy broadcasting
            if x.shape != y.shape:
                x, y = np.broadcast_arrays(x, y)

            shape = x.shape
            x = x.ravel()
            y = y.ravel()

            if x.size == 0 or y.size == 0:
                return np.zeros(shape, dtype=self.tck[2].dtype)

            if dx or dy:
                z,ier = dfitpack.pardeu(tx,ty,c,kx,ky,dx,dy,x,y)
                if not ier == 0:
                    raise ValueError("Error code returned by pardeu: %s" % ier)
            else:
                z,ier = dfitpack.bispeu(tx,ty,c,kx,ky,x,y)
                if not ier == 0:
                    raise ValueError("Error code returned by bispeu: %s" % ier)

            z = z.reshape(shape)
        return z