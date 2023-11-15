def set_bipolar_reference(inst, anode, cathode, ch_name=None, ch_info=None,
                          drop_refs=True, copy=True, verbose=None):
    """Re-reference selected channels using a bipolar referencing scheme.

    A bipolar reference takes the difference between two channels (the anode
    minus the cathode) and adds it as a new virtual channel. The original
    channels will be dropped.

    Multiple anodes and cathodes can be specified, in which case multiple
    virtual channels will be created. The 1st anode will be subtracted from the
    1st cathode, the 2nd anode from the 2nd cathode, etc.

    By default, the virtual channels will be annotated with channel info of
    the anodes, their locations set to (0, 0, 0) and coil types set to
    EEG_BIPOLAR.

    Parameters
    ----------
    inst : instance of Raw | Epochs | Evoked
        Data containing the unreferenced channels.
    anode : str | list of str
        The name(s) of the channel(s) to use as anode in the bipolar reference.
    cathode : str | list of str
        The name(s) of the channel(s) to use as cathode in the bipolar
        reference.
    ch_name : str | list of str | None
        The channel name(s) for the virtual channel(s) containing the resulting
        signal. By default, bipolar channels are named after the anode and
        cathode, but it is recommended to supply a more meaningful name.
    ch_info : dict | list of dict | None
        This parameter can be used to supply a dictionary (or a dictionary for
        each bipolar channel) containing channel information to merge in,
        overwriting the default values. Defaults to None.
    drop_refs : bool
        Whether to drop the anode/cathode channels from the instance.
    copy : bool
        Whether to operate on a copy of the data (True) or modify it in-place
        (False). Defaults to True.
    %(verbose)s

    Returns
    -------
    inst : instance of Raw | Epochs | Evoked
        Data with the specified channels re-referenced.

    See Also
    --------
    set_eeg_reference : Convenience function for creating an EEG reference.

    Notes
    -----
    1. If the anodes contain any EEG channels, this function removes
       any pre-existing average reference projections.

    2. During source localization, the EEG signal should have an average
       reference.

    3. The data must be preloaded.

    .. versionadded:: 0.9.0
    """
    _check_can_reref(inst)
    if not isinstance(anode, list):
        anode = [anode]

    if not isinstance(cathode, list):
        cathode = [cathode]

    if len(anode) != len(cathode):
        raise ValueError('Number of anodes (got %d) must equal the number '
                         'of cathodes (got %d).' % (len(anode), len(cathode)))

    if ch_name is None:
        ch_name = ['%s-%s' % ac for ac in zip(anode, cathode)]
    elif not isinstance(ch_name, list):
        ch_name = [ch_name]
    if len(ch_name) != len(anode):
        raise ValueError('Number of channel names must equal the number of '
                         'anodes/cathodes (got %d).' % len(ch_name))

    # Check for duplicate channel names (it is allowed to give the name of the
    # anode or cathode channel, as they will be replaced).
    for ch, a, c in zip(ch_name, anode, cathode):
        if ch not in [a, c] and ch in inst.ch_names:
            raise ValueError('There is already a channel named "%s", please '
                             'specify a different name for the bipolar '
                             'channel using the ch_name parameter.' % ch)

    if ch_info is None:
        ch_info = [{} for _ in anode]
    elif not isinstance(ch_info, list):
        ch_info = [ch_info]
    if len(ch_info) != len(anode):
        raise ValueError('Number of channel info dictionaries must equal the '
                         'number of anodes/cathodes.')

    # Merge specified and anode channel information dictionaries
    new_chs = []
    for ci, (an, ch) in enumerate(zip(anode, ch_info)):
        _check_ch_keys(ch, ci, name='ch_info', check_min=False)
        an_idx = inst.ch_names.index(an)
        this_chs = deepcopy(inst.info['chs'][an_idx])

        # Set channel location and coil type
        this_chs['loc'] = np.zeros(12)
        this_chs['coil_type'] = FIFF.FIFFV_COIL_EEG_BIPOLAR

        this_chs.update(ch)
        new_chs.append(this_chs)

    if copy:
        inst = inst.copy()

    for i, (an, ca, name, chs) in enumerate(
            zip(anode, cathode, ch_name, new_chs)):
        if an in anode[i + 1:] or an in cathode[i + 1:] or not drop_refs:
            # Make a copy of the channel if it's still needed later
            # otherwise it's modified inplace
            _copy_channel(inst, an, 'TMP')
            an = 'TMP'
        _apply_reference(inst, [ca], [an])  # ensures preloaded
        an_idx = inst.ch_names.index(an)
        inst.info['chs'][an_idx] = chs
        inst.info['chs'][an_idx]['ch_name'] = name
        logger.info('Bipolar channel added as "%s".' % name)
        inst.info._update_redundant()

    if getattr(inst, 'picks', None) is not None:
        del inst.picks  # picks cannot be tracked anymore

    # Drop remaining channels.
    if drop_refs:
        drop_channels = list((set(anode) | set(cathode)) & set(inst.ch_names))
        inst.drop_channels(drop_channels)

    return inst