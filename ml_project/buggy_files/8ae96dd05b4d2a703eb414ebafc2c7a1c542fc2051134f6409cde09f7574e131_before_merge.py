def _get_policy_object(platform,
                       filters=None,
                       pillar_key='acl',
                       pillarenv=None,
                       saltenv=None,
                       merge_pillar=True):
    '''
    Return an instance of the ``_Policy`` class given the filters config.
    '''
    policy = _Policy()
    policy_filters = []
    if not filters:
        filters = {}
    for filter_name, filter_config in six.iteritems(filters):
        header = aclgen.policy.Header()  # same header everywhere
        target_opts = [
            platform,
            filter_name
        ]
        filter_options = filter_config.pop('options', None)
        if filter_options:
            filter_options = _make_it_list(filter_options, filter_name, filter_options)
            # make sure the filter options are sent as list
            target_opts.extend(filter_options)
        target = aclgen.policy.Target(target_opts)
        header.AddObject(target)
        filter_terms = []
        for term_name, term_fields in six.iteritems(filter_config):
            term = _get_term_object(filter_name,
                                    term_name,
                                    pillar_key=pillar_key,
                                    pillarenv=pillarenv,
                                    saltenv=saltenv,
                                    merge_pillar=merge_pillar,
                                    **term_fields)
            filter_terms.append(term)
        policy_filters.append(
            (header, filter_terms)
        )
    policy.filters = policy_filters
    log.debug('Policy config:')
    log.debug(str(policy))
    platform_generator = _import_platform_generator(platform)
    policy_config = platform_generator(policy, 2)
    log.debug('Generating policy config for {platform}:'.format(
        platform=platform))
    log.debug(str(policy_config))
    return policy_config