    def _switch_ds(self, new_ds, data_source=None):
        old_object = self.data_source
        name = old_object._type_name
        kwargs = dict((n, getattr(old_object, n))
                      for n in old_object._con_args)
        kwargs['center'] = getattr(old_object, 'center', None)
        if data_source is not None:
            if name != "proj":
                raise RuntimeError("The data_source keyword argument "
                                   "is only defined for projections.")
            kwargs['data_source'] = data_source

        self.ds = new_ds

        # A _hack_ for ParticleProjectionPlots
        if name == 'Particle':
            from yt.visualization.particle_plots import \
            ParticleAxisAlignedDummyDataSource
            new_object = ParticleAxisAlignedDummyDataSource(ds=self.ds, **kwargs)
        else:
            new_object = getattr(new_ds, name)(**kwargs)

        self.data_source = new_object
        self._data_valid = self._plot_valid = False

        for d in 'xyz':
            lim_name = d+'lim'
            if hasattr(self, lim_name):
                lim = getattr(self, lim_name)
                lim = tuple(new_ds.quan(l.value, str(l.units)) for l in lim)
                setattr(self, lim_name, lim)
        self.plots.data_source = new_object
        self._colorbar_label.data_source = new_object
        self._setup_plots()