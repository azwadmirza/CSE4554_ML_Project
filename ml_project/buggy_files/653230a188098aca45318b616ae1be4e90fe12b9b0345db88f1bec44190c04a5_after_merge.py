    def meshgrid(self):
        """Return a meshgrid of numpy arrays for this mesh.

        This simply returns a ``numpy.meshgrid`` of the coordinates for this
        mesh in ``ij`` indexing. These are a copy of the points of this mesh.

        """
        return np.meshgrid(self.x, self.y, self.z, indexing='ij')