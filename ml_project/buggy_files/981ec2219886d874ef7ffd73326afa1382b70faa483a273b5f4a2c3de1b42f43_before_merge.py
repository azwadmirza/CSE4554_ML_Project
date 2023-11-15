    def deposit(self, positions, fields = None, method = None,
                kernel_name = 'cubic'):
        # Here we perform our particle deposition.
        cls = getattr(particle_deposit, "deposit_%s" % method, None)
        if cls is None:
            raise YTParticleDepositionNotImplemented(method)
        # We allocate number of zones, not number of octs
        # Everything inside this is fortran ordered, so we reverse it here.
        op = cls(tuple(self.ActiveDimensions)[::-1], kernel_name)
        op.initialize()
        op.process_grid(self, positions, fields)
        vals = op.finalize()
        if vals is None: return
        return vals.transpose() # Fortran-ordered, so transpose.