    def get_dataset(self, dsid, info, out=None):
        """Load a dataset."""

        logger.debug('Reading %s.', dsid.name)
        variable = self.nc[dsid.name]

        info = {'platform_name': self.platform_name,
                'sensor': self.sensor}

        try:
            values = np.ma.masked_equal(variable[:],
                                        variable.attrs['_FillValue'], copy=False)
        except KeyError:
            values = np.ma.array(variable[:], copy=False)
        if 'scale_factor' in variable.attrs:
            values = values * variable.attrs['scale_factor']
            info['scale_factor'] = variable.attrs['scale_factor']
        if 'add_offset' in variable.attrs:
            values = values + variable.attrs['add_offset']
            info['add_offset'] = variable.attrs['add_offset']
        if 'valid_range' in variable.attrs:
            info['valid_range'] = variable.attrs['valid_range']
        if 'units' in variable.attrs:
            info['units'] = variable.attrs['units']
        if 'standard_name' in variable.attrs:
            info['standard_name'] = variable.attrs['standard_name']

        if self.pps and dsid.name == 'ctth_alti':
            info['valid_range'] = (0., 8500.)
        if self.pps and dsid.name == 'ctth_alti_pal':
            values = values[1:, :]

        proj = Dataset(np.squeeze(values),
                       copy=False,
                       **info)
        return proj