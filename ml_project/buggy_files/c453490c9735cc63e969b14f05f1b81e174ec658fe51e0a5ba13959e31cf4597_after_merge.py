def low(data, **kwargs):
    '''
    Execute a single low data call
    This function is mostly intended for testing the state system

    CLI Example:

    .. code-block:: bash

        salt '*' state.low '{"state": "pkg", "fun": "installed", "name": "vi"}'
    '''
    st_kwargs = __salt__.kwargs
    __opts__['grains'] = __grains__
    chunks = [data]
    st_ = salt.client.ssh.state.SSHHighState(
            __opts__,
            __pillar__,
            __salt__,
            __context__['fileclient'])
    for chunk in chunks:
        chunk['__id__'] = chunk['name'] if not chunk.get('__id__') else chunk['__id__']
    err = st_.state.verify_data(data)
    if err:
        return err
    file_refs = salt.client.ssh.state.lowstate_file_refs(
            chunks,
            _merge_extra_filerefs(
                kwargs.get('extra_filerefs', ''),
                __opts__.get('extra_filerefs', '')
                )
            )
    roster = salt.roster.Roster(__opts__, __opts__.get('roster', 'flat'))
    roster_grains = roster.opts['grains']

    # Create the tar containing the state pkg and relevant files.
    trans_tar = salt.client.ssh.state.prep_trans_tar(
            __opts__,
            __context__['fileclient'],
            chunks,
            file_refs,
            __pillar__,
            st_kwargs['id_'],
            roster_grains)
    trans_tar_sum = salt.utils.hashutils.get_hash(trans_tar, __opts__['hash_type'])
    cmd = 'state.pkg {0}/salt_state.tgz pkg_sum={1} hash_type={2}'.format(
            __opts__['thin_dir'],
            trans_tar_sum,
            __opts__['hash_type'])
    single = salt.client.ssh.Single(
            __opts__,
            cmd,
            fsclient=__context__['fileclient'],
            minion_opts=__salt__.minion_opts,
            **st_kwargs)
    single.shell.send(
            trans_tar,
            '{0}/salt_state.tgz'.format(__opts__['thin_dir']))
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