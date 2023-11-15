    def __call__(self, datasets, **info):
        """Create the composite by scaling the DNB data using an adaptive histogram equalization method.

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
        has_multi_times = len(mixed_mask) > 0
        if day_mask.any():
            did_equalize = True
            if self.adaptive_day == "always" or (
                    has_multi_times and self.adaptive_day == "multiple"):
                LOG.debug("Adaptive histogram equalizing DNB day data...")
                local_histogram_equalization(
                    dnb_data.data,
                    day_mask,
                    valid_data_mask=good_mask,
                    local_radius_px=self.day_radius_pixels,
                    out=output_dataset)
            else:
                LOG.debug("Histogram equalizing DNB day data...")
                histogram_equalization(dnb_data.data,
                                       day_mask,
                                       out=output_dataset)
        if mixed_mask:
            for mask in mixed_mask:
                if mask.any():
                    did_equalize = True
                    if self.adaptive_mixed == "always" or (
                            has_multi_times and
                            self.adaptive_mixed == "multiple"):
                        LOG.debug(
                            "Adaptive histogram equalizing DNB mixed data...")
                        local_histogram_equalization(
                            dnb_data.data,
                            mask,
                            valid_data_mask=good_mask,
                            local_radius_px=self.mixed_radius_pixels,
                            out=output_dataset)
                    else:
                        LOG.debug("Histogram equalizing DNB mixed data...")
                        histogram_equalization(dnb_data.data,
                                               day_mask,
                                               out=output_dataset)
        if night_mask.any():
            did_equalize = True
            if self.adaptive_night == "always" or (
                    has_multi_times and self.adaptive_night == "multiple"):
                LOG.debug("Adaptive histogram equalizing DNB night data...")
                local_histogram_equalization(
                    dnb_data.data,
                    night_mask,
                    valid_data_mask=good_mask,
                    local_radius_px=self.night_radius_pixels,
                    out=output_dataset)
            else:
                LOG.debug("Histogram equalizing DNB night data...")
                histogram_equalization(dnb_data.data,
                                       night_mask,
                                       out=output_dataset)

        if not did_equalize:
            raise RuntimeError("No valid data found to histogram equalize")

        info = dnb_data.info.copy()
        info.update(self.attrs)
        info["standard_name"] = "equalized_radiance"
        info["mode"] = "L"
        output_dataset.info = info
        return output_dataset