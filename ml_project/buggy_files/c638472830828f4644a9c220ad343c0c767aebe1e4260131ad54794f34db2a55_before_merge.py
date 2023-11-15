def accept_vpc_peering_connection(name=None, conn_id=None, conn_name=None,
                                  region=None, key=None, keyid=None, profile=None):
    '''
    Accept a VPC pending requested peering connection between two VPCs.

    name
        Name of this state

    conn_id
        The connection ID to accept. Exclusive with conn_name. String type.

    conn_name
        The name of the VPC peering connection to accept. Exclusive with conn_id. String type.

    region
        Region to connect to.

    key
        Secret key to be used.

    keyid
        Access key to be used.

    profile
        A dict with region, key and keyid, or a pillar key (string) that
        contains a dict with region, key and keyid.

    .. versionadded:: 2016.11.0

    Example:

    .. code-block:: yaml

        boto_vpc.accept_vpc_peering_connection:
            - conn_name: salt_peering_connection

        # usage with vpc peering connection id and region
        boto_vpc.accept_vpc_peering_connection:
            - conn_id: pbx-1873d472
            - region: us-west-2

    '''
    log.debug('Called state to accept VPC peering connection')
    pending = __salt__['boto_vpc.is_peering_connection_pending'](
        conn_id=conn_id,
        conn_name=conn_name,
        region=region,
        key=key,
        keyid=keyid,
        profile=profile
    )

    ret = {
        'name': name,
        'result': True,
        'changes': {},
        'comment': 'Boto VPC peering state'
    }

    if not pending['exists']:
        ret['result'] = True
        ret['changes'].update({
            'old': 'No pending VPC peering connection found. '
                   'Nothing to be done.'
        })
        return ret

    if __opts__['test']:
        ret['changes'].update({'old': 'Pending VPC peering connection found '
                                      'and can be accepted'})
        return ret
    log.debug('Calling module to accept this VPC peering connection')
    result = __salt__['boto_vpc.accept_vpc_peering_connection'](
            conn_id=conn_id, name=conn_name, region=region, key=key,
            keyid=keyid, profile=profile)

    if 'error' in result:
        ret['comment'] = "Failed to request VPC peering: {0}".format(result['error'])
        ret['result'] = False
        return ret

    ret['changes'].update({
        'old': '',
        'new': result['msg']
    })

    return ret