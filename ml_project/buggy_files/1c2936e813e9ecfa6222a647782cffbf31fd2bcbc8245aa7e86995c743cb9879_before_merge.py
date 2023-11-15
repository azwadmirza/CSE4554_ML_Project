    def deposit(self, positions, fields = None, method = None,
                kernel_name='cubic'):
        r"""Operate on the mesh, in a particle-against-mesh fashion, with
        exclusively local input.

        This uses the octree indexing system to call a "deposition" operation
        (defined in yt/geometry/particle_deposit.pyx) that can take input from
        several particles (local to the mesh) and construct some value on the
        mesh.  The canonical example is to sum the total mass in a mesh cell
        and then divide by its volume.

        Parameters
        ----------
        positions : array_like (Nx3)
            The positions of all of the particles to be examined.  A new
            indexed octree will be constructed on these particles.
        fields : list of arrays
            All the necessary fields for computing the particle operation.  For
            instance, this might include mass, velocity, etc.
        method : string
            This is the "method name" which will be looked up in the
            `particle_deposit` namespace as `methodname_deposit`.  Current
            methods include `count`, `simple_smooth`, `sum`, `std`, `cic`,
            `weighted_mean`, `mesh_id`, and `nearest`.
        kernel_name : string, default 'cubic'
            This is the name of the smoothing kernel to use. Current supported
            kernel names include `cubic`, `quartic`, `quintic`, `wendland2`,
            `wendland4`, and `wendland6`.

        Returns
        -------
        List of fortran-ordered, mesh-like arrays.
        """
        # Here we perform our particle deposition.
        if fields is None: fields = []
        cls = getattr(particle_deposit, "deposit_%s" % method, None)
        if cls is None:
            raise YTParticleDepositionNotImplemented(method)
        nz = self.nz
        nvals = (nz, nz, nz, (self.domain_ind >= 0).sum())
        # We allocate number of zones, not number of octs
        op = cls(nvals, kernel_name)
        op.initialize()
        mylog.debug("Depositing %s (%s^3) particles into %s Octs",
            positions.shape[0], positions.shape[0]**0.3333333, nvals[-1])
        pos = np.asarray(positions.convert_to_units("code_length"),
                         dtype="float64")
        # We should not need the following if we know in advance all our fields
        # need no casting.
        fields = [np.asarray(f, dtype="float64") for f in fields]
        op.process_octree(self.oct_handler, self.domain_ind, pos, fields,
            self.domain_id, self._domain_offset)
        vals = op.finalize()
        if vals is None: return
        return np.asfortranarray(vals)