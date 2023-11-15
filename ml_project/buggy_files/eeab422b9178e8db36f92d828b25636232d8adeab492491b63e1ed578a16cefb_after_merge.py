def change_resource_record_sets(HostedZoneId=None, Name=None,
                                PrivateZone=None, ChangeBatch=None,
                                region=None, key=None, keyid=None, profile=None):
    '''
    Ugh!!!  Not gonna try to reproduce and validatethis mess in here - just pass what we get to AWS
    and let it decide if it's valid or not...

    See the `AWS Route53 API docs`__ as well as the `Boto3 documentation`__ for all the details...

    .. __: https://docs.aws.amazon.com/Route53/latest/APIReference/API_ChangeResourceRecordSets.html
    .. __: http://boto3.readthedocs.io/en/latest/reference/services/route53.html#Route53.Client.change_resource_record_sets

    The syntax for a ChangeBatch parameter is as follows, but note that the permutations of allowed
    parameters and combinations thereof are quite varied, so perusal of the above linked docs is
    highly recommended for any non-trival configurations.

    .. code-block:: json
    ChangeBatch={
        'Comment': 'string',
        'Changes': [
            {
                'Action': 'CREATE'|'DELETE'|'UPSERT',
                'ResourceRecordSet': {
                    'Name': 'string',
                    'Type': 'SOA'|'A'|'TXT'|'NS'|'CNAME'|'MX'|'NAPTR'|'PTR'|'SRV'|'SPF'|'AAAA',
                    'SetIdentifier': 'string',
                    'Weight': 123,
                    'Region': 'us-east-1'|'us-east-2'|'us-west-1'|'us-west-2'|'ca-central-1'|'eu-west-1'|'eu-west-2'|'eu-central-1'|'ap-southeast-1'|'ap-southeast-2'|'ap-northeast-1'|'ap-northeast-2'|'sa-east-1'|'cn-north-1'|'ap-south-1',
                    'GeoLocation': {
                        'ContinentCode': 'string',
                        'CountryCode': 'string',
                        'SubdivisionCode': 'string'
                    },
                    'Failover': 'PRIMARY'|'SECONDARY',
                    'TTL': 123,
                    'ResourceRecords': [
                        {
                            'Value': 'string'
                        },
                    ],
                    'AliasTarget': {
                        'HostedZoneId': 'string',
                        'DNSName': 'string',
                        'EvaluateTargetHealth': True|False
                    },
                    'HealthCheckId': 'string',
                    'TrafficPolicyInstanceId': 'string'
                }
            },
        ]
    }

    CLI Example:

    .. code-block:: bash

        foo='{
               "Name": "my-cname.example.org.",
               "TTL": 600,
               "Type": "CNAME",
               "ResourceRecords": [
                 {
                   "Value": "my-host.example.org"
                 }
               ]
             }'
        foo=`echo $foo`  # Remove newlines
        salt myminion boto3_route53.change_resource_record_sets DomainName=example.org. \
                keyid=A1234567890ABCDEF123 key=xblahblahblah \
                ChangeBatch="{'Changes': [{'Action': 'UPSERT', 'ResourceRecordSet': $foo}]}"
    '''
    if not _exactly_one((HostedZoneId, Name)):
        raise SaltInvocationError('Exactly one of either HostZoneId or Name must be provided.')
    if Name:
        args = {'Name': Name, 'region': region, 'key': key, 'keyid': keyid,
                'profile': profile}
        args.update({'PrivateZone': PrivateZone}) if PrivateZone is not None else None
        zone = find_hosted_zone(**args)
        if not zone:
            log.error("Couldn't resolve domain name {0} to a hosted zone ID.".format(Name))
            return []
        HostedZoneId = zone[0]['HostedZone']['Id']

    args = {'HostedZoneId': HostedZoneId, 'ChangeBatch': ChangeBatch}
    conn = _get_conn(region=region, key=key, keyid=keyid, profile=profile)
    tries = 20  # A bit more headroom
    while tries:
        try:
            r = conn.change_resource_record_sets(**args)
            return _wait_for_sync(r['ChangeInfo']['Id'], conn, 30)  # And a little extra time here
        except ClientError as e:
            if tries and e.response.get('Error', {}).get('Code') == 'Throttling':
                log.debug('Throttled by AWS API.')
                time.sleep(3)
                tries -= 1
                continue
            log.error('Failed to apply requested changes to the hosted zone {0}: {1}'.format(
                    Name or HostedZoneId, str(e)))
    return False