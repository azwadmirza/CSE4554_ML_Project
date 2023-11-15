    def __init__(self, filename, mode='r', clobber=True, diskless=False,
                 persist=False, format='NETCDF4', group=None):
        import netCDF4 as nc4
        ds = nc4.Dataset(filename, mode=mode, clobber=clobber,
                         diskless=diskless, persist=persist,
                         format=format)
        self.ds = _nc4_group(ds, group, mode)
        self.format = format
        self._filename = filename