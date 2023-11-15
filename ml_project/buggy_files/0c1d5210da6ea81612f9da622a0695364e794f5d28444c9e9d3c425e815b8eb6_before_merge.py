def _read_annotations_eeglab(eeg, uint16_codec=None):
    r"""Create Annotations from EEGLAB file.

    This function reads the event attribute from the EEGLAB
    structure and makes an :class:`mne.Annotations` object.

    Parameters
    ----------
    eeg : object | str
        'EEG' struct or the path to the (EEGLAB) .set file.
    uint16_codec : str | None
        If your \*.set file contains non-ascii characters, sometimes reading
        it may fail and give rise to error message stating that "buffer is
        too small". ``uint16_codec`` allows to specify what codec (for example:
        'latin1' or 'utf-8') should be used when reading character arrays and
        can therefore help you solve this problem.

    Returns
    -------
    annotations : instance of Annotations
        The annotations present in the file.
    """
    if isinstance(eeg, str):
        eeg = _check_load_mat(eeg, uint16_codec=uint16_codec)

    if not hasattr(eeg, 'event'):
        events = []
    elif isinstance(eeg.event, dict) and \
            np.array(eeg.event['latency']).ndim > 0:
        events = _dol_to_lod(eeg.event)
    elif not isinstance(eeg.event, (np.ndarray, list)):
        events = [eeg.event]
    else:
        events = eeg.event
    events = _bunchify(events)
    description = [str(event.type) for event in events]
    onset = [event.latency - 1 for event in events]
    duration = np.zeros(len(onset))
    if len(events) > 0 and hasattr(events[0], 'duration'):
        duration[:] = [event.duration for event in events]

    return Annotations(onset=np.array(onset) / eeg.srate,
                       duration=duration / eeg.srate,
                       description=description,
                       orig_time=None)