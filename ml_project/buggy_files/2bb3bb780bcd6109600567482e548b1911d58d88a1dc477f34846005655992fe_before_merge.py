    def __init__(self, dll):
        super(LGEOS330, self).__init__(dll)

        # GEOS 3.3.8 from homebrew has, but doesn't advertise
        # GEOSPolygonize_full. We patch it in explicitly here.
        key = 'GEOSPolygonize_full'
        func = getattr(self._lgeos, key + '_r')
        attr = ftools.partial(func, self.geos_handle)
        attr.__name__ = func.__name__
        setattr(self, key, attr)

        self.methods['unary_union'] = self.GEOSUnaryUnion
        self.methods['cascaded_union'] = self.methods['unary_union']