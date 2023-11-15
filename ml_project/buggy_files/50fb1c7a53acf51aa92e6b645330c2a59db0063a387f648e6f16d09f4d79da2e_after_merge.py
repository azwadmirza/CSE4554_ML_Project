    def __call__(self, projectables, **info):

        c01, c02, c03 = projectables

        # c02 = c02.sel(x=c01.coords['x'], y=c01.coords[
        #               'y'], method='nearest', tolerance=0.1)


        r = c02[::2, ::2]
        b = c01
        r.coords['x'] = b.coords['x']
        r.coords['y'] = b.coords['y']
        r.data = r.data.rechunk(b.chunks)
        g = simulated_green(c01, c02, c03)
        g.attrs = b.attrs
        g.coords['t'] = b.coords['t']
        del g.attrs['wavelength']

        return super(TrueColor2km, self).__call__((r, g, b), **info)