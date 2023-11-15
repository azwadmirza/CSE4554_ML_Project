def highstate(test=None, **kwargs):
    '''
    Retrieve the state data from the salt master for this minion and execute it

    CLI Example:

    .. code-block:: bash

        salt '*' state.highstate

        salt '*' state.highstate exclude=sls_to_exclude
        salt '*' state.highstate exclude="[{'id': 'id_to_exclude'}, {'sls': 'sls_to_exclude'}]"
    '''
    __pillar__.update(kwargs.get('pillar', {}))
    st_kwargs = __salt__.kwargs
    __opts__['grains'] = __grains__
    st_ = salt.client.ssh.state.SSHHighState(
            __opts__,
            __pillar__,
            __salt__,
            __context__['fileclient'])
    chunks = st_.compile_low_chunks()
    file_refs = salt.client.ssh.state.lowstate_file_refs(
            chunks,
            _merge_extra_filerefs(
                kwargs.get('extra_filerefs', ''),
                __opts__.get('extra_filerefs', '')
                )
            )
    # Check for errors
    for chunk in chunks:
        if not isinstance(chunk, dict):
            __context__['retcode'] = 1
            return chunks
    # Create the tar containing the state pkg and relevant files.
    trans_tar = salt.client.ssh.state.prep_trans_tar(
            __opts__,
            __context__['fileclient'],
            chunks,
            file_refs,
            __pillar__,
            st_kwargs['id_'])
    trans_tar_sum = salt.utils.get_hash(trans_tar, __opts__['hash_type'])
    cmd = 'state.pkg {0}/salt_state.tgz test={1} pkg_sum={2} hash_type={3}'.format(
            __opts__['thin_dir'],
            test,
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
        return json.loads(stdout, object_hook=salt.utils.decode_dict)
    except Exception as e:
        log.error("JSON Render failed for: {0}\n{1}".format(stdout, stderr))
        log.error(str(e))

    # If for some reason the json load fails, return the stdout
    return stdout