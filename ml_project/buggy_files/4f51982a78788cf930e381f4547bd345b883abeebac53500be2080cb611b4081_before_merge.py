def sls(mods, saltenv='base', test=None, exclude=None, **kwargs):
    '''
    Create the seed file for a state.sls run
    '''
    st_kwargs = __salt__.kwargs
    __opts__['grains'] = __grains__
    __pillar__.update(kwargs.get('pillar', {}))
    opts = salt.utils.state.get_sls_opts(__opts__, **kwargs)
    st_ = salt.client.ssh.state.SSHHighState(
            opts,
            __pillar__,
            __salt__,
            __context__['fileclient'])
    st_.push_active()
    if isinstance(mods, six.string_types):
        mods = mods.split(',')
    high_data, errors = st_.render_highstate({saltenv: mods})
    if exclude:
        if isinstance(exclude, six.string_types):
            exclude = exclude.split(',')
        if '__exclude__' in high_data:
            high_data['__exclude__'].extend(exclude)
        else:
            high_data['__exclude__'] = exclude
    high_data, ext_errors = st_.state.reconcile_extend(high_data)
    errors += ext_errors
    errors += st_.state.verify_high(high_data)
    if errors:
        return errors
    high_data, req_in_errors = st_.state.requisite_in(high_data)
    errors += req_in_errors
    high_data = st_.state.apply_exclude(high_data)
    # Verify that the high data is structurally sound
    if errors:
        return errors
    # Compile and verify the raw chunks
    chunks = st_.state.compile_high_data(high_data)
    file_refs = salt.client.ssh.state.lowstate_file_refs(
            chunks,
            _merge_extra_filerefs(
                kwargs.get('extra_filerefs', ''),
                opts.get('extra_filerefs', '')
                )
            )

    roster = salt.roster.Roster(opts, opts.get('roster', 'flat'))
    roster_grains = roster.opts['grains']

    # Create the tar containing the state pkg and relevant files.
    _cleanup_slsmod_low_data(chunks)
    trans_tar = salt.client.ssh.state.prep_trans_tar(
            opts,
            __context__['fileclient'],
            chunks,
            file_refs,
            __pillar__,
            st_kwargs['id_'],
            roster_grains)
    trans_tar_sum = salt.utils.hashutils.get_hash(trans_tar, opts['hash_type'])
    cmd = 'state.pkg {0}/salt_state.tgz test={1} pkg_sum={2} hash_type={3}'.format(
            opts['thin_dir'],
            test,
            trans_tar_sum,
            opts['hash_type'])
    single = salt.client.ssh.Single(
            opts,
            cmd,
            fsclient=__context__['fileclient'],
            minion_opts=__salt__.minion_opts,
            **st_kwargs)
    single.shell.send(
            trans_tar,
            '{0}/salt_state.tgz'.format(opts['thin_dir']))
    stdout, stderr, _ = single.cmd_block()

    # Clean up our tar
    try:
        os.remove(trans_tar)
    except (OSError, IOError):
        pass

    # Read in the JSON data and return the data structure
    try:
        return salt.utils.json.loads(stdout, object_hook=salt.utils.data.decode_dict)
    except Exception as e:
        log.error("JSON Render failed for: %s\n%s", stdout, stderr)
        log.error(six.text_type(e))

    # If for some reason the json load fails, return the stdout
    return stdout