def update_hosted_zone_comment(Id=None, Name=None, Comment=None, PrivateZone=None,
                               region=None, key=None, keyid=None, profile=None):
    '''
    Update the comment on an existing Route 53 hosted zone.

    Id
        The unique Zone Identifier for the Hosted Zone.

    Name
        The domain name associated with the Hosted Zone(s).

    Comment
        Any comments you want to include about the hosted zone.

    PrivateZone
        Boolean - Set to True if changing a private hosted zone.

    CLI Example::

        salt myminion boto3_route53.update_hosted_zone_comment Name=example.org. \
                Comment="This is an example comment for an example zone"
    '''
    if not _exactly_one((Id, Name)):
        raise SaltInvocationError('Exactly one of either Id or Name is required.')
    conn = _get_conn(region=region, key=key, keyid=keyid, profile=profile)
    if Name:
        args = {'Name': Name, 'PrivateZone': PrivateZone, 'region': region,
                'key': key, 'keyid': keyid, 'profile': profile}
        zone = find_hosted_zone(**args)
        if not zone:
            log.error("Couldn't resolve domain name {0} to a hosted zone ID.".format(Name))
            return []
        Id = zone[0]['HostedZone']['Id']
    tries = 10
    while tries:
        try:
            r = conn.update_hosted_zone_comment(Id=Id, Comment=Comment)
            r.pop('ResponseMetadata', None)
            return [r]
        except ClientError as e:
            if tries and e.response.get('Error', {}).get('Code') == 'Throttling':
                log.debug('Throttled by AWS API.')
                time.sleep(3)
                retries -= 1
                continue
            log.error('Failed to update comment on hosted zone {0}: {1}'.format(
                      Name or Id, str(e)))
    return []