    def recalculate_overall_sensitivity(self, frequency=None):
        """
        Recalculates the overall sensitivity.

        :param frequency: Choose frequency at which to calculate the
            sensitivity. If not given it will be chosen automatically.
        """
        if not hasattr(self, "instrument_sensitivity"):
            msg = "Could not find an instrument sensitivity - will not " \
                  "recalculate the overall sensitivity."
            raise ValueError(msg)

        if not self.instrument_sensitivity.input_units:
            msg = "Could not determine input units - will not " \
                  "recalculate the overall sensitivity."
            raise ValueError(msg)

        i_u = self.instrument_sensitivity.input_units

        unit_map = {
            "DISP": ["M"],
            "VEL": ["M/S", "M/SEC"],
            "ACC": ["M/S**2", "M/(S**2)", "M/SEC**2", "M/(SEC**2)",
                    "M/S/S"]}
        unit = None
        for key, value in unit_map.items():
            if i_u and i_u.upper() in value:
                unit = key
        if not unit:
            msg = ("ObsPy does not know how to map unit '%s' to "
                   "displacement, velocity, or acceleration - overall "
                   "sensitivity will not be recalculated.") % i_u
            raise ValueError(msg)

        # Determine frequency if not given.
        if frequency is None:
            # lookup normalization frequency of sensor's first stage it should
            # be in the flat part of the response
            stage_one = self.response_stages[0]
            try:
                frequency = stage_one.normalization_frequency
            except AttributeError:
                pass
            for stage in self.response_stages[::-1]:
                # determine sampling rate
                try:
                    sampling_rate = (stage.decimation_input_sample_rate /
                                     stage.decimation_factor)
                    break
                except Exception:
                    continue
            else:
                sampling_rate = None
            if sampling_rate:
                # if sensor's normalization frequency is above 0.5 * nyquist,
                # use that instead (e.g. to avoid computing an overall
                # sensitivity above nyquist)
                nyquist = sampling_rate / 2.0
                if frequency:
                    frequency = min(frequency, nyquist / 2.0)
                else:
                    frequency = nyquist / 2.0

        if frequency is None:
            msg = ("Could not automatically determine a suitable frequency "
                   "at which to calculate the sensitivity. The overall "
                   "sensitivity will not be recalculated.")
            raise ValueError(msg)

        freq, gain = self._get_overall_sensitivity_and_gain(
            output=unit, frequency=float(frequency))

        self.instrument_sensitivity.value = gain
        self.instrument_sensitivity.frequency = freq