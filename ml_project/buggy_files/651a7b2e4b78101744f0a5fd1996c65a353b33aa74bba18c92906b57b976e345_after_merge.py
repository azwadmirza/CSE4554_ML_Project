    def __call__(self, datasets, **info):
        if len(datasets) != 4:
            raise ValueError("Expected 4 datasets, got %d" % (len(datasets), ))

        from scipy.special import erf
        dnb_data = datasets[0]
        sza_data = datasets[1]
        lza_data = datasets[2]
        good_mask = ~(dnb_data.mask | sza_data.mask)
        output_dataset = dnb_data.copy()
        output_dataset.mask = ~good_mask
        # this algorithm assumes units of "W cm-2 sr-1" so if there are other
        # units we need to adjust for that
        if dnb_data.info.get("units", "W m-2 sr-1") == "W m-2 sr-1":
            unit_factor = 10000.
        else:
            unit_factor = 1.

        # convert to decimal instead of %
        moon_illum_fraction = np.mean(datasets[3]) * 0.01

        # From Steve Miller and Curtis Seaman
        # maxval = 10.^(-1.7 - (((2.65+moon_factor1+moon_factor2))*(1+erf((solar_zenith-95.)/(5.*sqrt(2.0))))))
        # minval = 10.^(-4. - ((2.95+moon_factor2)*(1+erf((solar_zenith-95.)/(5.*sqrt(2.0))))))
        # scaled_radiance = (radiance - minval) / (maxval - minval)
        # radiance = sqrt(scaled_radiance)

        # Version 2: Update from Curtis Seaman
        # maxval = 10.^(-1.7 - (((2.65+moon_factor1+moon_factor2))*(1+erf((solar_zenith-95.)/(5.*sqrt(2.0))))))
        # minval = 10.^(-4. - ((2.95+moon_factor2)*(1+erf((solar_zenith-95.)/(5.*sqrt(2.0))))))
        # saturated_pixels = where(radiance gt maxval, nsatpx)
        # saturation_pct = float(nsatpx)/float(n_elements(radiance))
        # print, 'Saturation (%) = ', saturation_pct
        #
        # while saturation_pct gt 0.005 do begin
        #   maxval = maxval*1.1
        #   saturated_pixels = where(radiance gt maxval, nsatpx)
        #   saturation_pct = float(nsatpx)/float(n_elements(radiance))
        #   print, saturation_pct
        # endwhile
        #
        # scaled_radiance = (radiance - minval) / (maxval - minval)
        # radiance = sqrt(scaled_radiance)

        moon_factor1 = 0.7 * (1.0 - moon_illum_fraction)
        moon_factor2 = 0.0022 * lza_data
        erf_portion = 1 + erf((sza_data - 95.0) / (5.0 * np.sqrt(2.0)))
        max_val = np.power(
            10, -1.7 -
            (2.65 + moon_factor1 + moon_factor2) * erf_portion) * unit_factor
        min_val = np.power(10, -4.0 -
                           (2.95 + moon_factor2) * erf_portion) * unit_factor

        # Update from Curtis Seaman, increase max radiance curve until less
        # than 0.5% is saturated
        if self.saturation_correction:
            saturation_pct = float(np.count_nonzero(dnb_data >
                                                    max_val)) / dnb_data.size
            LOG.debug("Dynamic DNB saturation percentage: %f", saturation_pct)
            while saturation_pct > 0.005:
                max_val *= 1.1 * unit_factor
                saturation_pct = float(np.count_nonzero(
                    dnb_data > max_val)) / dnb_data.size
                LOG.debug("Dynamic DNB saturation percentage: %f",
                          saturation_pct)

        inner_sqrt = (dnb_data - min_val) / (max_val - min_val)
        # clip negative values to 0 before the sqrt
        inner_sqrt[inner_sqrt < 0] = 0
        np.sqrt(inner_sqrt, out=output_dataset)

        info = dnb_data.info.copy()
        info.update(self.attrs)
        info["standard_name"] = "equalized_radiance"
        info["mode"] = "L"
        output_dataset.info = info
        return output_dataset