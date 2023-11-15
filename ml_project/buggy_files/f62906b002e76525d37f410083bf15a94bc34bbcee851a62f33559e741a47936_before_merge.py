def present(
        name,
        listeners,
        availability_zones=None,
        subnets=None,
        security_groups=None,
        scheme='internet-facing',
        health_check=None,
        attributes=None,
        attributes_from_pillar="boto_elb_attributes",
        cnames=None,
        alarms=None,
        alarms_from_pillar="boto_elb_alarms",
        policies=None,
        policies_from_pillar="boto_elb_policies",
        backends=None,
        region=None,
        key=None,
        keyid=None,
        profile=None,
        wait_for_sync=True,
        tags=None):
    '''
    Ensure the ELB exists.

    name
        Name of the ELB.

    availability_zones
        A list of availability zones for this ELB.

    listeners
        A list of listener lists; example::

            [
                ['443', 'HTTPS', 'arn:aws:iam::1111111:server-certificate/mycert'],
                ['8443', '80', 'HTTPS', 'HTTP', 'arn:aws:iam::1111111:server-certificate/mycert']
            ]

    subnets
        A list of subnet IDs in your VPC to attach to your LoadBalancer.

    security_groups
        The security groups assigned to your LoadBalancer within your VPC.

    scheme
        The type of a LoadBalancer. internet-facing or internal. Once set, can not be modified.

    health_check
        A dict defining the health check for this ELB.

    attributes
        A dict defining the attributes to set on this ELB.

    attributes_from_pillar
        name of pillar dict that contains attributes.   Attributes defined for this specific
        state will override those from pillar.

    cnames
        A list of cname dicts with attributes needed for the DNS add_record state.
        By default the boto_route53.add_record state will be used, which requires: name, zone, ttl, and identifier.
        See the boto_route53 state for information about these attributes.
        Other DNS modules can be called by specifying the provider keyword.
        the cnames dict will be passed to the state as kwargs.

    alarms:
        a dictionary of name->boto_cloudwatch_alarm sections to be associated with this ELB.
        All attributes should be specified except for dimension which will be
        automatically set to this ELB.
        See the boto_cloudwatch_alarm state for information about these attributes.

    alarms_from_pillar:
        name of pillar dict that contains alarm settings.   Alarms defined for this specific
        state will override those from pillar.

    region
        Region to connect to.

    key
        Secret key to be used.

    keyid
        Access key to be used.

    profile
        A dict with region, key and keyid, or a pillar key (string)
        that contains a dict with region, key and keyid.

    wait_for_sync
        Wait for an INSYNC change status from Route53.

    tags
        dict of tags
    '''

    # load data from attributes_from_pillar and merge with attributes
    tmp = __salt__['config.option'](attributes_from_pillar, {})
    if attributes:
        attributes = dictupdate.update(tmp, attributes)
    else:
        attributes = tmp

    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}
    _ret = _elb_present(name, availability_zones, listeners, subnets,
                        security_groups, scheme, region, key, keyid, profile)
    ret['changes'] = _ret['changes']
    ret['comment'] = ' '.join([ret['comment'], _ret['comment']])
    if not _ret['result']:
        ret['result'] = _ret['result']
        if ret['result'] is False:
            return ret

    if attributes:
        _ret = _attributes_present(name, attributes, region, key, keyid, profile)
        ret['changes'] = dictupdate.update(ret['changes'], _ret['changes'])
        ret['comment'] = ' '.join([ret['comment'], _ret['comment']])

        if not _ret['result']:
            ret['result'] = _ret['result']
            if ret['result'] is False:
                return ret

    _ret = _health_check_present(name, health_check, region, key, keyid,
                                 profile)
    ret['changes'] = dictupdate.update(ret['changes'], _ret['changes'])
    ret['comment'] = ' '.join([ret['comment'], _ret['comment']])
    if not _ret['result']:
        ret['result'] = _ret['result']
        if ret['result'] is False:
            return ret
    if cnames:
        lb = __salt__['boto_elb.get_elb_config'](
            name, region, key, keyid, profile
        )
        if len(lb) > 0:
            for cname in cnames:
                _ret = None
                dns_provider = 'boto_route53'
                cname['record_type'] = 'CNAME'
                cname['value'] = lb['dns_name']
                if 'provider' in cname:
                    dns_provider = cname.pop('provider')
                if dns_provider == 'boto_route53':
                    if 'profile' not in cname:
                        cname['profile'] = profile
                    if 'key' not in cname:
                        cname['key'] = key
                    if 'keyid' not in cname:
                        cname['keyid'] = keyid
                    if 'region' not in cname:
                        cname['region'] = region
                    if 'wait_for_sync' not in cname:
                        cname['wait_for_sync'] = wait_for_sync
                _ret = __states__['.'.join([dns_provider, 'present'])](**cname)
                ret['changes'] = dictupdate.update(ret['changes'], _ret['changes'])
                ret['comment'] = ' '.join([ret['comment'], _ret['comment']])
                if not _ret['result']:
                    ret['result'] = _ret['result']
                    if ret['result'] is False:
                        return ret

    _ret = _alarms_present(name, alarms, alarms_from_pillar, region, key, keyid, profile)
    ret['changes'] = dictupdate.update(ret['changes'], _ret['changes'])
    ret['comment'] = ' '.join([ret['comment'], _ret['comment']])
    if not _ret['result']:
        ret['result'] = _ret['result']
        if ret['result'] is False:
            return ret
    _ret = _policies_present(name, policies, policies_from_pillar, listeners,
                             backends, region, key, keyid, profile)
    ret['changes'] = dictupdate.update(ret['changes'], _ret['changes'])
    ret['comment'] = ' '.join([ret['comment'], _ret['comment']])
    if not _ret['result']:
        ret['result'] = _ret['result']
        if ret['result'] is False:
            return ret
    _ret = _tags_present(name, tags, region, key, keyid, profile)
    ret['changes'] = dictupdate.update(ret['changes'], _ret['changes'])
    ret['comment'] = ' '.join([ret['comment'], _ret['comment']])
    if not _ret['result']:
        ret['result'] = _ret['result']
        if ret['result'] is False:
            return ret
    return ret