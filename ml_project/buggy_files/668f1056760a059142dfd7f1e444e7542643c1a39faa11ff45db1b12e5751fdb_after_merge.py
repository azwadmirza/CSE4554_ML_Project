def _read_curry_parameters(fname):
    """Extract Curry params from a Curry info file."""
    _msg_match = "The sampling frequency and the time steps extracted from " \
                 "the parameter file do not match."
    _msg_invalid = "sfreq must be greater than 0. Got sfreq = {0}"

    var_names = ['NumSamples', 'SampleFreqHz',
                 'DataFormat', 'SampleTimeUsec',
                 'NumChannels',
                 'StartYear', 'StartMonth', 'StartDay', 'StartHour',
                 'StartMin', 'StartSec', 'StartMillisec',
                 'NUM_SAMPLES', 'SAMPLE_FREQ_HZ',
                 'DATA_FORMAT', 'SAMPLE_TIME_USEC',
                 'NUM_CHANNELS',
                 'START_YEAR', 'START_MONTH', 'START_DAY', 'START_HOUR',
                 'START_MIN', 'START_SEC', 'START_MILLISEC']

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

    # look for CHAN_IN_FILE sections, which may or may not exist; issue #8391
    types = ["meg", "eeg", "misc"]
    chanidx_in_file = _read_curry_lines(fname,
                                        ["CHAN_IN_FILE" +
                                         CHANTYPES[key] for key in types])

    n_samples = int(param_dict["numsamples"])
    sfreq = float(param_dict["samplefreqhz"])
    time_step = float(param_dict["sampletimeusec"]) * 1e-6
    is_ascii = param_dict["dataformat"] == "ASCII"
    n_channels = int(param_dict["numchannels"])
    try:
        dt_start = datetime(int(param_dict["startyear"]),
                            int(param_dict["startmonth"]),
                            int(param_dict["startday"]),
                            int(param_dict["starthour"]),
                            int(param_dict["startmin"]),
                            int(param_dict["startsec"]),
                            int(param_dict["startmillisec"]) * 1000,
                            timezone.utc)
        # Note that the time zone information is not stored in the Curry info
        # file, and it seems the start time info is in the local timezone
        # of the acquisition system (which is unknown); therefore, just set
        # the timezone to be UTC.  If the user knows otherwise, they can
        # change it later.  (Some Curry files might include StartOffsetUTCMin,
        # but its presence is unpredictable, so we won't rely on it.)
    except (ValueError, KeyError):
        dt_start = None  # if missing keywords or illegal values, don't set

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

    return CurryParameters(n_samples, true_sfreq, is_ascii, unit_dict,
                           n_channels, dt_start, chanidx_in_file)