def setval(key, val):
    '''
    Set a grains value in the grains config file

    CLI Example:

    .. code-block:: bash

        salt '*' grains.setval key val
        salt '*' grains.setval key "{'sub-key': 'val', 'sub-key2': 'val2'}"
    '''
    grains = {}
    if os.path.isfile(__opts__['conf_file']):
        gfn = os.path.join(
            os.path.dirname(__opts__['conf_file']),
            'grains'
        )
    elif os.path.isdir(__opts__['conf_file']):
        gfn = os.path.join(
            __opts__['conf_file'],
            'grains'
        )
    else:
        gfn = os.path.join(
            os.path.dirname(__opts__['conf_file']),
            'grains'
        )

    if os.path.isfile(gfn):
        with salt.utils.fopen(gfn, 'rb') as fp_:
            try:
                grains = yaml.safe_load(fp_.read())
            except Exception as e:
                return 'Unable to read existing grains file: {0}'.format(e)
        if not isinstance(grains, dict):
            grains = {}
    grains[key] = val
    cstr = yaml.safe_dump(grains, default_flow_style=False)
    with salt.utils.fopen(gfn, 'w+') as fp_:
        fp_.write(cstr)
    fn_ = os.path.join(__opts__['cachedir'], 'module_refresh')
    with salt.utils.fopen(fn_, 'w+') as fp_:
        fp_.write('')
    # Sync the grains
    __salt__['saltutil.sync_grains']()
    # Return the grain we just set to confirm everything was OK
    return {key: val}