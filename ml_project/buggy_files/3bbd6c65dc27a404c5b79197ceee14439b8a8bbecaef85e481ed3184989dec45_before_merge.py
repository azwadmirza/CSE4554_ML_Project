def anonymize_info(info, daysback=None, keep_his=False, verbose=None):
    """Anonymize measurement information in place.

    .. warning:: If ``info`` is part of an object like
                 :class:`raw.info <mne.io.Raw>`, you should directly use
                 the method :meth:`raw.anonymize() <mne.io.Raw.anonymize>`
                 to ensure that all parts of the data are anonymized and
                 stay synchronized (e.g.,
                 :class:`raw.annotations <mne.Annotations>`).

    Parameters
    ----------
    info : dict, instance of Info
        Measurement information for the dataset.
    %(anonymize_info_parameters)s
    %(verbose)s

    Returns
    -------
    info : instance of Info
        The anonymized measurement information.

    Notes
    -----
    %(anonymize_info_notes)s
    """
    _validate_type(info, 'info', "self")

    default_anon_dos = datetime.datetime(2000, 1, 1, 0, 0, 0,
                                         tzinfo=datetime.timezone.utc)
    default_str = "mne_anonymize"
    default_subject_id = 0
    default_desc = ("Anonymized using a time shift"
                    " to preserve age at acquisition")

    none_meas_date = info['meas_date'] is None

    if none_meas_date:
        warn('Input info has \'meas_date\' set to None.'
             ' Removing all information from time/date structures.'
             ' *NOT* performing any time shifts')
        info['meas_date'] = None
    else:
        # compute timeshift delta
        if daysback is None:
            delta_t = info['meas_date'] - default_anon_dos
        else:
            delta_t = datetime.timedelta(days=daysback)
        # adjust meas_date
        info['meas_date'] = info['meas_date'] - delta_t

    # file_id and meas_id
    for key in ('file_id', 'meas_id'):
        value = info.get(key)
        if value is not None:
            assert 'msecs' not in value
            if none_meas_date:
                tmp = DATE_NONE
            else:
                tmp = _add_timedelta_to_stamp(
                    (value['secs'], value['usecs']), -delta_t)
            value['secs'] = tmp[0]
            value['usecs'] = tmp[1]
            # The following copy is needed for a test CTF dataset
            # otherwise value['machid'][:] = 0 would suffice
            _tmp = value['machid'].copy()
            _tmp[:] = 0
            value['machid'] = _tmp

    # subject info
    subject_info = info.get('subject_info')
    if subject_info is not None:
        if subject_info.get('id') is not None:
            subject_info['id'] = default_subject_id
        if keep_his:
            logger.info('Not fully anonymizing info - keeping \'his_id\'')
        elif subject_info.get('his_id') is not None:
            subject_info['his_id'] = str(default_subject_id)

        for key in ('last_name', 'first_name', 'middle_name'):
            if subject_info.get(key) is not None:
                subject_info[key] = default_str

        # anonymize the subject birthday
        if none_meas_date:
            subject_info.pop('birthday', None)
        elif subject_info.get('birthday') is not None:
            dob = datetime.datetime(subject_info['birthday'][0],
                                    subject_info['birthday'][1],
                                    subject_info['birthday'][2])
            dob -= delta_t
            subject_info['birthday'] = dob.year, dob.month, dob.day

        for key in ('weight', 'height'):
            if subject_info.get(key) is not None:
                subject_info[key] = 0

    info['experimenter'] = default_str
    info['description'] = default_desc

    if info['proj_id'] is not None:
        info['proj_id'] = np.zeros_like(info['proj_id'])
    if info['proj_name'] is not None:
        info['proj_name'] = default_str
    if info['utc_offset'] is not None:
        info['utc_offset'] = None

    proc_hist = info.get('proc_history')
    if proc_hist is not None:
        for record in proc_hist:
            record['block_id']['machid'][:] = 0
            record['experimenter'] = default_str
            if none_meas_date:
                record['block_id']['secs'] = DATE_NONE[0]
                record['block_id']['usecs'] = DATE_NONE[1]
                record['date'] = DATE_NONE
            else:
                this_t0 = (record['block_id']['secs'],
                           record['block_id']['usecs'])
                this_t1 = _add_timedelta_to_stamp(
                    this_t0, -delta_t)
                record['block_id']['secs'] = this_t1[0]
                record['block_id']['usecs'] = this_t1[1]
                record['date'] = _add_timedelta_to_stamp(
                    record['date'], -delta_t)

    hi = info.get('helium_info')
    if hi is not None:
        if hi.get('orig_file_guid') is not None:
            hi['orig_file_guid'] = default_str
        if none_meas_date and hi.get('meas_date') is not None:
            hi['meas_date'] = DATE_NONE
        elif hi.get('meas_date') is not None:
            hi['meas_date'] = _add_timedelta_to_stamp(
                hi['meas_date'], -delta_t)

    di = info.get('device_info')
    if di is not None:
        for k in ('serial', 'site'):
            if di.get(k) is not None:
                di[k] = default_str

    err_mesg = ('anonymize_info generated an inconsistent info object. '
                'Underlying Error:\n')
    info._check_consistency(prepend_error=err_mesg)
    err_mesg = ('anonymize_info generated an inconsistent info object. '
                'daysback parameter was too large.'
                'Underlying Error:\n')
    _check_dates(info, prepend_error=err_mesg)

    return info