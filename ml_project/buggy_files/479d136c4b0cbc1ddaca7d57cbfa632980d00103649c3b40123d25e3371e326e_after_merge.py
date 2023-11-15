def record_absent(name, zone, type, data, profile):
    '''
    Ensures a record is absent.

    :param name: Record name without the domain name (e.g. www).
                 Note: If you want to create a record for a base domain
                 name, you should specify empty string ('') for this
                 argument.
    :type  name: ``str``

    :param zone: Zone where the requested record is created, the domain name
    :type  zone: ``str``

    :param type: DNS record type (A, AAAA, ...).
    :type  type: ``str``

    :param data: Data for the record (depends on the record type).
    :type  data: ``str``

    :param profile: The profile key
    :type  profile: ``str``
    '''
    zones = __salt__['libcloud_dns.list_zones'](profile)
    try:
        matching_zone = [z for z in zones if z.domain == zone][0]
    except IndexError:
        return state_result(False, "Zone could not be found")
    records = __salt__['libcloud_dns.list_records'](matching_zone.id, profile)
    matching_records = [record for record in records
                        if record.name == name and
                        record.type == type and
                        record.data == data]
    if len(matching_records) > 0:
        result = []
        for record in matching_records:
            result.append(__salt__['libcloud_dns.delete_record'](
                matching_zone.id,
                record.id,
                profile))
        return state_result(all(result), "Removed {0} records".format(len(result)))
    else:
        return state_result(True, "Records already absent")