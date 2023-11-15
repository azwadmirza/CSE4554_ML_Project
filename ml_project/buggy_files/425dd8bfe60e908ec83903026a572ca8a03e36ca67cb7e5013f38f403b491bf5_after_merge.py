def zone_absent(domain, profile):
    '''
    Ensures a record is absent.

    :param domain: Zone name, i.e. the domain name
    :type  domain: ``str``

    :param profile: The profile key
    :type  profile: ``str``
    '''
    zones = __salt__['libcloud_dns.list_zones'](profile)
    matching_zone = [z for z in zones if z.domain == domain]
    if len(matching_zone) == 0:
        return state_result(True, "Zone already absent")
    else:
        result = __salt__['libcloud_dns.delete_zone'](matching_zone[0].id, profile)
        return state_result(result, "Deleted zone")