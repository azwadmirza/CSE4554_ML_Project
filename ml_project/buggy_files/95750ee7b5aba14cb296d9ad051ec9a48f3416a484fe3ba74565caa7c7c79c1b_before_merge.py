def absent(
        name,
        zone,
        record_type,
        identifier=None,
        region=None,
        key=None,
        keyid=None,
        profile=None,
        wait_for_sync=True,
        split_dns=False,
        private_zone=False):
    '''
    Ensure the Route53 record is deleted.

    name
        Name of the record.

    zone
        The zone to delete the record from.

    record_type
        The record type (A, NS, MX, TXT, etc.)

    identifier
        An identifier to match for deletion.

    region
        The region to connect to.

    key
        Secret key to be used.

    keyid
        Access key to be used.

    profile
        A dict with region, key and keyid, or a pillar key (string)
        that contains a dict with region, key and keyid.

    wait_for_sync
        Wait for an INSYNC change status from Route53.

    split_dns
        Route53 supports a public and private DNS zone with the same
        names.

    private_zone
        If using split_dns, specify if this is the private zone.
    '''
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}

    record = __salt__['boto_route53.get_record'](name, zone, record_type,
                                                 False, region, key, keyid,
                                                 profile, split_dns,
                                                 private_zone)
    if record:
        if __opts__['test']:
            msg = 'Route53 record {0} set to be deleted.'.format(name)
            ret['comment'] = msg
            ret['result'] = None
            return ret
        deleted = __salt__['boto_route53.delete_record'](name, zone,
                                                         record_type,
                                                         identifier, False,
                                                         region, key, keyid,
                                                         profile,
                                                         wait_for_sync,
                                                         split_dns,
                                                         private_zone)
        if deleted:
            ret['changes']['old'] = record
            ret['changes']['new'] = None
            ret['comment'] = 'Deleted {0} Route53 record.'.format(name)
        else:
            ret['result'] = False
            msg = 'Failed to delete {0} Route53 record.'.format(name)
            ret['comment'] = msg
    else:
        ret['comment'] = '{0} does not exist.'.format(name)
    return ret