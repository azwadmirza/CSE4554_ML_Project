    def points(self, points):
        """Set points without copying."""
        if not isinstance(points, np.ndarray):
            raise TypeError('Points must be a numpy array')
        # get the unique coordinates along each axial direction
        x = np.unique(points[:,0])
        y = np.unique(points[:,1])
        z = np.unique(points[:,2])
        nx, ny, nz = len(x), len(y), len(z)
        # diff returns an empty array if the input is constant
        dx, dy, dz = [np.diff(d) if len(np.diff(d)) > 0 else d for d in (x, y, z)]
        # TODO: this needs to be tested (unique might return a tuple)
        dx, dy, dz = np.unique(dx), np.unique(dy), np.unique(dz)
        ox, oy, oz = np.min(x), np.min(y), np.min(z)
        # Build the vtk object
        self._from_specs((nx,ny,nz), (dx,dy,dz), (ox,oy,oz))
        #self._point_ref = points
        self.Modified()