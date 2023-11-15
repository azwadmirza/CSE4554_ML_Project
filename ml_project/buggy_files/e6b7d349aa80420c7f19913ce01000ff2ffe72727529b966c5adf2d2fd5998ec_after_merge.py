    def __call__(self, datasets, **info):
        if len(datasets) != 4:
            raise ValueError("Expected 4 datasets, got %d" % (len(datasets), ))

        dnb_data = datasets[0]
        sza_data = datasets[1]
        lza_data = datasets[2]
        #good_mask = ~(dnb_data.mask | sza_data.mask)
        #output_dataset = dnb_data.copy()
        #output_dataset.mask = ~good_mask
        # this algorithm assumes units of "W cm-2 sr-1" so if there are other
        # units we need to adjust for that
        if dnb_data.info.get("units", "W m-2 sr-1") == "W m-2 sr-1":
            unit_factor = 10000.
        else:
            unit_factor = 1.

        mda = dnb_data.info.copy()

        dnb_data = dnb_data / unit_factor

        # convert to decimal instead of %
        moon_illum_fraction = np.mean(datasets[3]) * 0.01

        phi = np.rad2deg(np.arccos(2. * moon_illum_fraction - 1))

        vfl = 0.026 * phi + 4.0e-9 * (phi ** 4.)

        m_fullmoon = -12.74
        m_sun = -26.74
        m_moon = vfl + m_fullmoon

        gs_ = self.gain_factor(sza_data)

        r_sun_moon = 10.**((m_sun - m_moon) / -2.5)
        gl_ = r_sun_moon * self.gain_factor(lza_data)
        gtot = 1. / (1. / gs_ + 1. / gl_)

        dnb_data += 2.6e-10
        dnb_data *= gtot

        mda['name'] = self.attrs['name']
        mda.pop('calibration')
        mda.pop('wavelength')
        mda['standard_name'] = 'ncc_radiance'

        return Dataset(dnb_data, copy=False, **mda)