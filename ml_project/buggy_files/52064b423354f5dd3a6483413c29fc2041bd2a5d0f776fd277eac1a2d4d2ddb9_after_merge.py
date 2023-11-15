def present(
        name,
        value,
        zone,
        record_type,
        ttl=None,
        identifier=None,
        region=None,
        key=None,
        keyid=None,
        profile=None):
    '''
    Ensure the Route53 record is present.

    name
        Name of the record.

    value
        Value of the record.

    zone
        The zone to create the record in.

    record_type
        The record type. Currently supported values: A, CNAME, MX

    ttl
        The time to live for the record.

    identifier
        The unique identifier to use for this record.

    region
        The region to connect to.

    key
        Secret key to be used.

    keyid
        Access key to be used.

    profile
        A dict with region, key and keyid, or a pillar key (string)
        that contains a dict with region, key and keyid.
    '''
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}

    # If a list is passed in for value, change it to a comma-separated string
    # So it will work with subsequent boto module calls and string functions
    if isinstance(value, list):
        value = ','.join(value)

    record = __salt__['boto_route53.get_record'](name, zone, record_type,
                                                 False, region, key, keyid,
                                                 profile)

    if isinstance(record, dict) and not record:
        if __opts__['test']:
            ret['comment'] = 'Route53 record {0} set to be added.'.format(name)
            ret['result'] = None
            return ret
        added = __salt__['boto_route53.add_record'](name, value, zone,
                                                    record_type, identifier,
                                                    ttl, region, key, keyid,
                                                    profile)
        if added:
            ret['changes']['old'] = None
            ret['changes']['new'] = {'name': name,
                                     'value': value,
                                     'record_type': record_type,
                                     'ttl': ttl}
            ret['comment'] = 'Added {0} Route53 record.'.format(name)
        else:
            ret['result'] = False
            ret['comment'] = 'Failed to add {0} Route53 record.'.format(name)
            return ret
    elif record:
        need_to_update = False
        # Values can be a comma separated list and some values will end with a
        # period (even if we set it without one). To easily check this we need
        # to split and check with the period stripped from the input and what's
        # in route53.
        # TODO: figure out if this will cause us problems with some records.
        _values = [x.rstrip('.') for x in value.split(',')]
        _r_values = [x.rstrip('.') for x in record['value'].split(',')]
        _values.sort()
        _r_values.sort()
        if _values != _r_values:
            need_to_update = True
        if identifier and identifier != record['identifier']:
            need_to_update = True
        if ttl and str(ttl) != str(record['ttl']):
            need_to_update = True
        if need_to_update:
            if __opts__['test']:
                msg = 'Route53 record {0} set to be updated.'.format(name)
                ret['comment'] = msg
                ret['result'] = None
                return ret
            updated = __salt__['boto_route53.update_record'](name, value, zone,
                                                             record_type,
                                                             identifier, ttl,
                                                             region, key,
                                                             keyid, profile)
            if updated:
                ret['changes']['old'] = record
                ret['changes']['new'] = {'name': name,
                                         'value': value,
                                         'record_type': record_type,
                                         'ttl': ttl}
                ret['comment'] = 'Updated {0} Route53 record.'.format(name)
            else:
                ret['result'] = False
                msg = 'Failed to update {0} Route53 record.'.format(name)
                ret['comment'] = msg
        else:
            ret['comment'] = '{0} exists.'.format(name)
    return ret