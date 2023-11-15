def pkg(pkg_path,
        pkg_sum,
        hash_type,
        test=None,
        **kwargs):
    '''
    Execute a packaged state run, the packaged state run will exist in a
    tarball available locally. This packaged state
    can be generated using salt-ssh.

    CLI Example:

    .. code-block:: bash

        salt '*' state.pkg /tmp/salt_state.tgz 760a9353810e36f6d81416366fc426dc md5
    '''
    # TODO - Add ability to download from salt master or other source
    popts = salt.utils.state.get_sls_opts(__opts__, **kwargs)
    if not os.path.isfile(pkg_path):
        return {}
    if not salt.utils.hashutils.get_hash(pkg_path, hash_type) == pkg_sum:
        return {}
    root = tempfile.mkdtemp()
    s_pkg = tarfile.open(pkg_path, 'r:gz')
    # Verify that the tarball does not extract outside of the intended root
    members = s_pkg.getmembers()
    for member in members:
        if member.path.startswith((os.sep, '..{0}'.format(os.sep))):
            return {}
        elif '..{0}'.format(os.sep) in member.path:
            return {}
    s_pkg.extractall(root)
    s_pkg.close()
    lowstate_json = os.path.join(root, 'lowstate.json')
    with salt.utils.files.fopen(lowstate_json, 'r') as fp_:
        lowstate = salt.utils.json.load(fp_)
    # Check for errors in the lowstate
    for chunk in lowstate:
        if not isinstance(chunk, dict):
            return lowstate
    pillar_json = os.path.join(root, 'pillar.json')
    if os.path.isfile(pillar_json):
        with salt.utils.files.fopen(pillar_json, 'r') as fp_:
            pillar_override = salt.utils.json.load(fp_)
    else:
        pillar_override = None

    roster_grains_json = os.path.join(root, 'roster_grains.json')
    if os.path.isfile(roster_grains_json):
        with salt.utils.files.fopen(roster_grains_json, 'r') as fp_:
            roster_grains = salt.utils.json.load(fp_)

    if os.path.isfile(roster_grains_json):
        popts['grains'] = roster_grains
    popts['fileclient'] = 'local'
    popts['file_roots'] = {}
    popts['test'] = _get_test_value(test, **kwargs)
    envs = os.listdir(root)
    for fn_ in envs:
        full = os.path.join(root, fn_)
        if not os.path.isdir(full):
            continue
        popts['file_roots'][fn_] = [full]
    st_ = salt.state.State(popts, pillar_override=pillar_override)
    snapper_pre = _snapper_pre(popts, kwargs.get('__pub_jid', 'called localy'))
    ret = st_.call_chunks(lowstate)
    ret = st_.call_listen(lowstate, ret)
    try:
        shutil.rmtree(root)
    except (IOError, OSError):
        pass
    _set_retcode(ret)
    _snapper_post(popts, kwargs.get('__pub_jid', 'called localy'), snapper_pre)
    return ret