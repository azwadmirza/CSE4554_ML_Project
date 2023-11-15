def record_present(name, zone, type, data, profile):
    '''
    Ensures a record is present.

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
    zones = libcloud_dns_module.list_zones(profile)
    try:
        matching_zone = [z for z in zones if z.domain == zone][0]
    except IndexError:
        return state_result(False, "Could not locate zone")
    records = libcloud_dns_module.list_records(matching_zone.id, profile)
    matching_records = [record for record in records
                        if record.name == name and
                        record.type == type and
                        record.data == data]
    if len(matching_records) == 0:
        result = libcloud_dns_module.create_record(
            name, matching_zone.id,
            type, data, profile)
        return state_result(result, "Created new record")
    else:
        return state_result(True, "Record already exists")