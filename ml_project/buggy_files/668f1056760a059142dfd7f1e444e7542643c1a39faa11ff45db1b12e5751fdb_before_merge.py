def _read_curry_parameters(fname):
    """Extract Curry params from a Curry info file."""
    _msg_match = "The sampling frequency and the time steps extracted from " \
                 "the parameter file do not match."
    _msg_invalid = "sfreq must be greater than 0. Got sfreq = {0}"

    var_names = ['NumSamples', 'SampleFreqHz',
                 'DataFormat', 'SampleTimeUsec',
                 'NUM_SAMPLES', 'SAMPLE_FREQ_HZ',
                 'DATA_FORMAT', 'SAMPLE_TIME_USEC']

    param_dict = dict()
    unit_dict = dict()
    with open(fname) as fid:
        for line in iter(fid):
            if any(var_name in line for var_name in var_names):
                key, val = line.replace(" ", "").replace("\n", "").split("=")
                param_dict[key.lower().replace("_", "")] = val
            for type in CHANTYPES:
                if "DEVICE_PARAMETERS" + CHANTYPES[type] + " START" in line:
                    data_unit = next(fid)
                    unit_dict[type] = data_unit.replace(" ", "") \
                        .replace("\n", "").split("=")[-1]

    n_samples = int(param_dict["numsamples"])
    sfreq = float(param_dict["samplefreqhz"])
    time_step = float(param_dict["sampletimeusec"]) * 1e-6
    is_ascii = param_dict["dataformat"] == "ASCII"

    if time_step == 0:
        true_sfreq = sfreq
    elif sfreq == 0:
        true_sfreq = 1 / time_step
    elif not np.isclose(sfreq, 1 / time_step):
        raise ValueError(_msg_match)
    else:  # they're equal and != 0
        true_sfreq = sfreq
    if true_sfreq <= 0:
        raise ValueError(_msg_invalid.format(true_sfreq))

    return CurryParameters(n_samples, true_sfreq, is_ascii, unit_dict)