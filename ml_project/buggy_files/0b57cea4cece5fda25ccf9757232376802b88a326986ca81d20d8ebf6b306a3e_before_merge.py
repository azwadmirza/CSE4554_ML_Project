    def deposit(self, positions, fields = None, method = None,
                kernel_name = 'cubic'):
        cls = getattr(particle_deposit, "deposit_%s" % method, None)
        if cls is None:
            raise YTParticleDepositionNotImplemented(method)
        # We allocate number of zones, not number of octs
        op = cls(self.ActiveDimensions, kernel_name)
        op.initialize()
        op.process_grid(self, positions, fields)
        vals = op.finalize()
        return vals.copy(order="C")