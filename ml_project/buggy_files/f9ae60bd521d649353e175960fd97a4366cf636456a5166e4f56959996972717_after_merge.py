def high(data, **kwargs):
    '''
    Execute the compound calls stored in a single set of high data
    This function is mostly intended for testing the state system

    CLI Example:

    .. code-block:: bash

        salt '*' state.high '{"vim": {"pkg": ["installed"]}}'
    '''
    __pillar__.update(kwargs.get('pillar', {}))
    st_kwargs = __salt__.kwargs
    __opts__['grains'] = __grains__
    opts = salt.utils.state.get_sls_opts(__opts__, **kwargs)
    st_ = salt.client.ssh.state.SSHHighState(
            opts,
            __pillar__,
            __salt__,
            __context__['fileclient'])
    st_.push_active()
    chunks = st_.state.compile_high_data(data)
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
    cmd = 'state.pkg {0}/salt_state.tgz pkg_sum={1} hash_type={2}'.format(
            opts['thin_dir'],
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
        return salt.utils.json.loads(stdout)
    except Exception as e:
        log.error("JSON Render failed for: %s\n%s", stdout, stderr)
        log.error(six.text_type(e))

    # If for some reason the json load fails, return the stdout
    return stdout