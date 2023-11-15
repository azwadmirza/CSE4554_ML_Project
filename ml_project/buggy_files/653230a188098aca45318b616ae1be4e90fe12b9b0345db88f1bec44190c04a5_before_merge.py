    def meshgrid(self):
        """Return the a meshgrid of numpy arrays for this mesh.

        This simply returns a ``numpy.meshgrid`` of the coordinates for this
        mesh in ``ij`` indexing.

        """
        return np.meshgrid(self.x, self.y, self.z, indexing='ij')