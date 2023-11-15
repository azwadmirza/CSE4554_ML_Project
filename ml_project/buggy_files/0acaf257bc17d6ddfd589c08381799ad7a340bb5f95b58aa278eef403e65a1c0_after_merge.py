    def query_object_async(self, wavelength_range=None, wavelength_type='',
                           wavelength_accuracy=None, element_spectrum=None,
                           minimal_abundance=None, depl_factor=None,
                           lower_level_energy_range=None,
                           upper_level_energy_range=None, nmax=None,
                           multiplet=None, transitions=None,
                           show_fine_structure=None,
                           show_auto_ionizing_transitions=None,
                           output_columns=('spec', 'type', 'conf',
                                           'term', 'angm', 'prob',
                                           'ener')):
        """
        Returns
        -------
        response : `requests.Response`
            The HTTP response returned from the service.
        """
        if self._default_form_values is None:
            response = self._request("GET", url=self.FORM_URL, data={},
                                     timeout=self.TIMEOUT)
            bs = BeautifulSoup(response.text)
            form = bs.find('form')
            self._default_form_values = self._get_default_form_values(form)
        default_values = self._default_form_values
        wltype = (wavelength_type or default_values.get('air', '')).lower()
        if wltype in ('air', 'vacuum'):
            air = wltype.capitalize()
        else:
            raise ValueError('parameter wavelength_type must be either "air" '
                             'or "vacuum".')
        if wavelength_range is not None:
            wlrange = wavelength_range
        else:
            wlrange = []
        if len(wlrange) not in (0, 2):
            raise ValueError('Length of `wavelength_range` must be 2 or 0, '
                             'but is: {}'.format(len(wlrange)))
        if not is_valid_transitions_param(transitions):
            raise ValueError('Invalid parameter "transitions": {0!r}'
                             .format(transitions))
        if transitions is None:
            _type = self._default_form_values.get('type')
            type2 = self._default_form_values.get('type2')
        else:
            s = str(transitions)
            if len(s.split(',')) > 1:
                _type = 'Sel'
                type2 = s.split(',')
            else:
                _type = s
                type2 = ''
        # convert wavelengths in incoming wavelength range to Angstroms
        wlrange_in_angstroms = (wl.to(u.Angstrom,
                                      equivalencies=u.spectral()).value
                                for wl in wlrange)

        lower_level_erange = lower_level_energy_range
        if lower_level_erange is not None:
            lower_level_erange = lower_level_erange.to(
                u.cm ** -1, equivalencies=u.spectral()).value
        upper_level_erange = upper_level_energy_range
        if upper_level_erange is not None:
            upper_level_erange = upper_level_erange.to(
                u.cm ** -1, equivalencies=u.spectral()).value
        input = {
            'wavl': '-'.join(map(str, wlrange_in_angstroms)),
            'wave': 'Angstrom',
            'air': air,
            'wacc': wavelength_accuracy,
            'elmion': element_spectrum,
            'abun': minimal_abundance,
            'depl': depl_factor,
            'elo': lower_level_erange,
            'ehi': upper_level_erange,
            'ener': 'cm^-1',
            'nmax': nmax,
            'term': multiplet,
            'type': _type,
            'type2': type2,
            'hydr': show_fine_structure,
            'auto': show_auto_ionizing_transitions,
            'form': output_columns,
            'tptype': 'as_a'}
        response = self._submit_form(input)
        return response