def single(fun, name, test=None, **kwargs):
    '''
    .. versionadded:: 2015.5.0

    Execute a single state function with the named kwargs, returns False if
    insufficient data is sent to the command

    By default, the values of the kwargs will be parsed as YAML. So, you can
    specify lists values, or lists of single entry key-value maps, as you
    would in a YAML salt file. Alternatively, JSON format of keyword values
    is also supported.

    CLI Example:

    .. code-block:: bash

        salt '*' state.single pkg.installed name=vim

    '''
    st_kwargs = __salt__.kwargs
    __opts__['grains'] = __grains__

    # state.fun -> [state, fun]
    comps = fun.split('.')
    if len(comps) < 2:
        __context__['retcode'] = 1
        return 'Invalid function passed'

    # Create the low chunk, using kwargs as a base
    kwargs.update({'state': comps[0],
                   'fun': comps[1],
                   '__id__': name,
                   'name': name})

    opts = salt.utils.state.get_sls_opts(__opts__, **kwargs)

    # Set test mode
    if salt.utils.args.test_mode(test=test, **kwargs):
        opts['test'] = True
    else:
        opts['test'] = __opts__.get('test', None)

    # Get the override pillar data
    __pillar__.update(kwargs.get('pillar', {}))

    # Create the State environment
    st_ = salt.client.ssh.state.SSHState(opts, __pillar__)

    # Verify the low chunk
    err = st_.verify_data(kwargs)
    if err:
        __context__['retcode'] = 1
        return err

    # Must be a list of low-chunks
    chunks = [kwargs]

    # Retrieve file refs for the state run, so we can copy relevant files down
    # to the minion before executing the state
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
    trans_tar = salt.client.ssh.state.prep_trans_tar(
            opts,
            __context__['fileclient'],
            chunks,
            file_refs,
            __pillar__,
            st_kwargs['id_'],
            roster_grains)

    # Create a hash so we can verify the tar on the target system
    trans_tar_sum = salt.utils.hashutils.get_hash(trans_tar, opts['hash_type'])

    # We use state.pkg to execute the "state package"
    cmd = 'state.pkg {0}/salt_state.tgz test={1} pkg_sum={2} hash_type={3}'.format(
            opts['thin_dir'],
            test,
            trans_tar_sum,
            opts['hash_type'])

    # Create a salt-ssh Single object to actually do the ssh work
    single = salt.client.ssh.Single(
            opts,
            cmd,
            fsclient=__context__['fileclient'],
            minion_opts=__salt__.minion_opts,
            **st_kwargs)

    # Copy the tar down
    single.shell.send(
            trans_tar,
            '{0}/salt_state.tgz'.format(opts['thin_dir']))

    # Run the state.pkg command on the target
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