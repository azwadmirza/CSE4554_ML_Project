    def get_dataset(self, dsid, info):
        """Load a dataset."""
        logger.debug('Reading %s.', dsid.name)
        variable = self.nc[dsid.name]

        variable = remove_empties(variable)

        if 'scale_factor' in variable.attrs or 'add_offset' in variable.attrs:
            scale = variable.attrs.get('scale_factor', 1)
            offset = variable.attrs.get('add_offset', 0)
            if np.issubdtype((scale + offset).dtype, np.floating):
                if '_FillValue' in variable.attrs:
                    variable = variable.where(
                        variable != variable.attrs['_FillValue'])
                if 'valid_range' in variable.attrs:
                    variable = variable.where(
                        variable <= variable.attrs['valid_range'][1])
                    variable = variable.where(
                        variable >= variable.attrs['valid_range'][0])
                if 'valid_max' in variable.attrs:
                    variable = variable.where(
                        variable <= variable.attrs['valid_max'])
                if 'valid_min' in variable.attrs:
                    variable = variable.where(
                        variable >= variable.attrs['valid_min'])

            variable = variable * scale + offset

        variable.attrs.update({'platform_name': self.platform_name,
                               'sensor': self.sensor})

        variable.attrs.setdefault('units', '1')

        ancillary_names = variable.attrs.get('ancillary_variables', '')
        try:
            variable.attrs['ancillary_variables'] = ancillary_names.split()
        except AttributeError:
            pass

        if 'standard_name' in info:
            variable.attrs.setdefault('standard_name', info['standard_name'])

        if self.pps and dsid.name == 'ctth_alti':
            variable.attrs['valid_range'] = (0., 8500.)
        if self.pps and dsid.name == 'ctth_alti_pal':
            variable = variable[1:, :]

        return variable