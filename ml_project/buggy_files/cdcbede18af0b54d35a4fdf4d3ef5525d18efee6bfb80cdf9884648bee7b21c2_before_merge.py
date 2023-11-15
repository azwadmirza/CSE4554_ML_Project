    def __call__(self, datasets, **info):
        """Create the composite by scaling the DNB data using a histogram equalization method.

        :param datasets: 2-element tuple (Day/Night Band data, Solar Zenith Angle data)
        :param **info: Miscellaneous metadata for the newly produced composite
        """
        if len(datasets) != 2:
            raise ValueError("Expected 2 datasets, got %d" % (len(datasets), ))

        dnb_data = datasets[0]
        sza_data = datasets[1]
        good_mask = ~(dnb_data.mask | sza_data.mask)
        output_dataset = dnb_data.copy()
        output_dataset.mask = ~good_mask
        day_mask, mixed_mask, night_mask = make_day_night_masks(
            sza_data,
            good_mask,
            self.high_angle_cutoff,
            self.low_angle_cutoff,
            stepsDegrees=self.mixed_degree_step)

        did_equalize = False
        if day_mask.any():
            LOG.debug("Histogram equalizing DNB day data...")
            histogram_equalization(dnb_data.data, day_mask, out=output_dataset)
            did_equalize = True
        if mixed_mask:
            for mask in mixed_mask:
                if mask.any():
                    LOG.debug("Histogram equalizing DNB mixed data...")
                    histogram_equalization(dnb_data.data,
                                           mask,
                                           out=output_dataset)
                    did_equalize = True
        if night_mask.any():
            LOG.debug("Histogram equalizing DNB night data...")
            histogram_equalization(dnb_data.data,
                                   night_mask,
                                   out=output_dataset)
            did_equalize = True

        if not did_equalize:
            raise RuntimeError("No valid data found to histogram equalize")

        info = dnb_data.info.copy()
        info.update(self.info)
        info["standard_name"] = "equalized_radiance"
        info["mode"] = "L"
        output_dataset.info = info
        return output_dataset