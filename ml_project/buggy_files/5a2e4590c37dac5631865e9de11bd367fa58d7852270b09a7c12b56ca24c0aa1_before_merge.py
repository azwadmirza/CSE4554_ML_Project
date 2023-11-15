def associate_vpc_with_hosted_zone(HostedZoneId=None, Name=None, VPCId=None,
                                   VPCName=None, VPCRegion=None, Comment=None,
                                   region=None, key=None, keyid=None, profile=None):
    '''
    Associates an Amazon VPC with a private hosted zone.

    To perform the association, the VPC and the private hosted zone must already exist. You can't
    convert a public hosted zone into a private hosted zone.  If you want to associate a VPC from
    one AWS account with a zone from a another, the AWS account owning the hosted zone must first
    submit a CreateVPCAssociationAuthorization (using create_vpc_association_authorization() or by
    other means, such as the AWS console).  With that done, the account owning the VPC can then call
    associate_vpc_with_hosted_zone() to create the association.

    Note that if both sides happen to be within the same account, associate_vpc_with_hosted_zone()
    is enough on its own, and there is no need for the CreateVPCAssociationAuthorization step.

    Also note that looking up hosted zones by name (e.g. using the Name parameter) only works
    within a single account - if you're associating a VPC to a zone in a different account, as
    outlined above, you unfortunately MUST use the HostedZoneId parameter exclusively.

    HostedZoneId
        The unique Zone Identifier for the Hosted Zone.

    Name
        The domain name associated with the Hosted Zone(s).

    VPCId
        When working with a private hosted zone, either the VPC ID or VPC Name to associate with is
        required.  Exclusive with VPCName.

    VPCName
        When working with a private hosted zone, either the VPC ID or VPC Name to associate with is
        required.  Exclusive with VPCId.

    VPCRegion
        When working with a private hosted zone, the region of the associated VPC is required.  If
        not provided, an effort will be made to determine it from VPCId or VPCName, if possible.  If
        this fails, you'll need to provide an explicit value for VPCRegion.

    Comment
        Any comments you want to include about the change being made.

    CLI Example::

        salt myminion boto3_route53.associate_vpc_with_hosted_zone \
                    Name=example.org. VPCName=myVPC \
                    VPCRegion=us-east-1 Comment="Whoo-hoo!  I added another VPC."

    '''
    if not _exactly_one((HostedZoneId, Name)):
        raise SaltInvocationError('Exactly one of either HostedZoneId or Name is required.')
    if not _exactly_one((VPCId, VPCName)):
        raise SaltInvocationError('Exactly one of either VPCId or VPCName is required.')
    if Name:
        # {'PrivateZone': True} because you can only associate VPCs with private hosted zones.
        args = {'Name': Name, 'PrivateZone': True, 'region': region,
                'key': key, 'keyid': keyid, 'profile': profile}
        zone = find_hosted_zone(**args)
        if not zone:
            log.error("Couldn't resolve domain name {0} to a private hosted zone"
                      'ID.'.format(Name))
            return False
        HostedZoneId = zone[0]['HostedZone']['Id']
    vpcs = __salt__['boto_vpc.describe_vpcs'](vpc_id=VPCId, name=VPCName, region=region, key=key,
                                              keyid=keyid, profile=profile).get('vpcs', [])
    if VPCRegion and vpcs:
        vpcs = [v for v in vpcs if v['region'] == VPCRegion]
    if not vpcs:
        log.error('No VPC matching the given criteria found.')
        return False
    if len(vpcs) > 1:
        log.error('Multiple VPCs matching the given criteria found: {0}.'
                  ''.format(', '.join([v['id'] for v in vpcs])))
        return False
    vpc = vpcs[0]
    if VPCName:
        VPCId = vpc['id']
    if not VPCRegion:
        VPCRegion = vpc['region']
    args = {'HostedZoneId': HostedZoneId, 'VPC': {'VPCId': VPCId, 'VPCRegion': VPCRegion}}
    args.update({'Comment': Comment}) if Comment is not None else None

    conn = _get_conn(region=region, key=key, keyid=keyid, profile=profile)
    tries = 10
    while tries:
        try:
            r = conn.associate_vpc_with_hosted_zone(**args)
            return _wait_for_sync(r['ChangeInfo']['Id'], conn)
        except ClientError as e:
            if tries and e.response.get('Error', {}).get('Code') == 'Throttling':
                log.debug('Throttled by AWS API.')
                time.sleep(3)
                retries -= 1
                continue
            log.error('Failed to associate VPC {0} with hosted zone {1}: {2}'.format(
                      VPCName or VPCId, Name or HostedZoneId, str(e)))
    return False