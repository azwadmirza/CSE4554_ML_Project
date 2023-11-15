def get_configured_provider(vm_=None):
    '''
    Return the contextual provider of None if no configured
    one can be found.
    '''
    if vm_ is None:
        vm_ = {}
    dalias, driver = __active_provider_name__.split(':')
    data = None
    tgt = 'unknown'
    img_provider = __opts__.get('list_images', '')
    arg_providers = __opts__.get('names', [])
    matched = False
    # --list-images level
    if img_provider:
        tgt = 'provider: {0}'.format(img_provider)
        if dalias == img_provider:
            data = get_provider(img_provider)
            matched = True
    # providers are set in configuration
    if not data and 'profile' not in __opts__ and arg_providers:
        for name in arg_providers:
            tgt = 'provider: {0}'.format(name)
            if dalias == name:
                data = get_provider(name)
            if data:
                matched = True
                break
    # -p is providen, get the uplinked provider
    elif 'profile' in __opts__:
        curprof = __opts__['profile']
        profs = __opts__['profiles']
        tgt = 'profile: {0}'.format(curprof)
        if (
            curprof in profs
            and profs[curprof]['provider'] == __active_provider_name__
        ):
            prov, cdriver = profs[curprof]['provider'].split(':')
            tgt += ' provider: {0}'.format(prov)
            data = get_provider(prov)
            matched = True
    # fallback if we have only __active_provider_name__
    if ((__opts__.get('destroy', False) and not data)
        or (not matched and __active_provider_name__)):
        data = __opts__.get('providers',
                           {}).get(dalias, {}).get(driver, {})
    # in all cases, verify that the linked saltmaster is alive.
    if data:
        try:
            ret = _salt('test.ping', salt_target=data['target'])
            if not ret:
                raise Exception('error')
            return data
        except Exception:
            raise SaltCloudSystemExit(
                'Configured provider {0} minion: {1} is unreachable'.format(
                    __active_provider_name__, data['target']))
    return False