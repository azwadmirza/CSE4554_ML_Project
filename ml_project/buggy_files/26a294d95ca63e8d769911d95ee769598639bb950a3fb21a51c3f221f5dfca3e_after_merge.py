def create_hosted_zone(Name, VPCId=None, VPCName=None, VPCRegion=None, CallerReference=None,
                       Comment='', PrivateZone=False, DelegationSetId=None,
                       region=None, key=None, keyid=None, profile=None):
    '''
    Create a new Route53 Hosted Zone. Returns a Python data structure with information about the
    newly created Hosted Zone.

    Name
        The name of the domain. This should be a fully-specified domain, and should terminate with
        a period. This is the name you have registered with your DNS registrar. It is also the name
        you will delegate from your registrar to the Amazon Route 53 delegation servers returned in
        response to this request.

    VPCId
        When creating a private hosted zone, either the VPC ID or VPC Name to associate with is
        required.  Exclusive with VPCName.  Ignored if passed for a non-private zone.

    VPCName
        When creating a private hosted zone, either the VPC ID or VPC Name to associate with is
        required.  Exclusive with VPCId.  Ignored if passed for a non-private zone.

    VPCRegion
        When creating a private hosted zone, the region of the associated VPC is required.  If not
        provided, an effort will be made to determine it from VPCId or VPCName, if possible.  If
        this fails, you'll need to provide an explicit value for this option.  Ignored if passed for
        a non-private zone.

    CallerReference
        A unique string that identifies the request and that allows create_hosted_zone() calls to be
        retried without the risk of executing the operation twice.  This is a required parameter
        when creating new Hosted Zones.  Maximum length of 128.

    Comment
        Any comments you want to include about the hosted zone.

    PrivateZone
        Boolean - Set to True if creating a private hosted zone.

    DelegationSetId
        If you want to associate a reusable delegation set with this hosted zone, the ID that Amazon
        Route 53 assigned to the reusable delegation set when you created it.  Note that XXX TODO
        create_delegation_set() is not yet implemented, so you'd need to manually create any
        delegation sets before utilizing this.

    region
        Region endpoint to connect to.

    key
        AWS key to bind with.

    keyid
        AWS keyid to bind with.

    profile
        Dict, or pillar key pointing to a dict, containing AWS region/key/keyid.

    CLI Example::

        salt myminion boto3_route53.create_hosted_zone example.org.
    '''
    if not Name.endswith('.'):
        raise SaltInvocationError('Domain must be fully-qualified, complete with trailing period.')
    conn = _get_conn(region=region, key=key, keyid=keyid, profile=profile)
    deets = find_hosted_zone(Name=Name, PrivateZone=PrivateZone,
                             region=region, key=key, keyid=keyid, profile=profile)
    if deets:
        log.info('Route 53 hosted zone {0} already exists.  You may want to pass e.g. '
                 "'PrivateZone=True' or similar...".format(Name))
        return None
    args = {
            'Name': Name,
            'CallerReference': CallerReference,
            'HostedZoneConfig': {
              'Comment': Comment,
              'PrivateZone': PrivateZone
            }
          }
    args.update({'DelegationSetId': DelegationSetId}) if DelegationSetId else None
    if PrivateZone:
        if not _exactly_one((VPCName, VPCId)):
            raise SaltInvocationError('Either VPCName or VPCId is required when creating a '
                                      'private zone.')
        vpcs = __salt__['boto_vpc.describe_vpcs'](
                vpc_id=VPCId, name=VPCName, region=region, key=key,
                keyid=keyid, profile=profile).get('vpcs', [])
        if VPCRegion and vpcs:
            vpcs = [v for v in vpcs if v['region'] == VPCRegion]
        if not vpcs:
            log.error('Private zone requested but no VPC matching given criteria found.')
            return None
        if len(vpcs) > 1:
            log.error('Private zone requested but multiple VPCs matching given criteria found: '
                      '{0}.'.format([v['id'] for v in vpcs]))
            return None
        vpc = vpcs[0]
        if VPCName:
            VPCId = vpc['id']
        if not VPCRegion:
            VPCRegion = vpc['region']
        args.update({'VPC': {'VPCId': VPCId, 'VPCRegion': VPCRegion}})
    else:
        if any((VPCId, VPCName, VPCRegion)):
            log.info('Options VPCId, VPCName, and VPCRegion are ignored when creating '
                     'non-private zones.')
    tries = 10
    while tries:
        try:
            r = conn.create_hosted_zone(**args)
            r.pop('ResponseMetadata', None)
            if _wait_for_sync(r['ChangeInfo']['Id'], conn):
                return [r]
            return []
        except ClientError as e:
            if tries and e.response.get('Error', {}).get('Code') == 'Throttling':
                log.debug('Throttled by AWS API.')
                time.sleep(3)
                tries -= 1
                continue
            log.error('Failed to create hosted zone {0}: {1}'.format(Name, str(e)))
            return []
    return []