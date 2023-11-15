def zone_present(domain, type, profile):
    '''
    Ensures a record is present.

    :param domain: Zone name, i.e. the domain name
    :type  domain: ``str``

    :param type: Zone type (master / slave), defaults to master
    :type  type: ``str``

    :param profile: The profile key
    :type  profile: ``str``
    '''
    zones = __salt__['libcloud_dns.list_zones'](profile)
    if not type:
        type = 'master'
    matching_zone = [z for z in zones if z.domain == domain]
    if len(matching_zone) > 0:
        return state_result(True, "Zone already exists")
    else:
        result = __salt__['libcloud_dns.create_zone'](domain, profile, type)
        return state_result(result, "Created new zone")