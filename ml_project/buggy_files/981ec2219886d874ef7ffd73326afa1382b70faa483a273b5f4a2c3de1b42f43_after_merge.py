    def deposit(self, positions, fields = None, method = None,
                kernel_name = 'cubic'):
        # Here we perform our particle deposition.
        cls = getattr(particle_deposit, "deposit_%s" % method, None)
        if cls is None:
            raise YTParticleDepositionNotImplemented(method)
        # We allocate number of zones, not number of octs. Everything inside
        # this is Fortran ordered because of the ordering in the octree deposit
        # routines, so we reverse it here to match the convention there
        op = cls(tuple(self.ActiveDimensions[::-1]), kernel_name)
        op.initialize()
        op.process_grid(self, positions, fields)
        vals = op.finalize()
        if vals is None: return
        # Fortran-ordered, so transpose.
        return vals.transpose()