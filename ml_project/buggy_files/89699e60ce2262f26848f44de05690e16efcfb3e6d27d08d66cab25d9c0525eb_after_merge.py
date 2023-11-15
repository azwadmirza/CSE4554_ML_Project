def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            vpc_id=dict(),
            peer_vpc_id=dict(),
            peer_region=dict(),
            peering_id=dict(),
            peer_owner_id=dict(),
            tags=dict(required=False, type='dict'),
            profile=dict(),
            state=dict(default='present', choices=['present', 'absent', 'accept', 'reject'])
        )
    )
    required_if = [
        ('state', 'present', ['vpc_id', 'peer_vpc_id']),
        ('state', 'accept', ['peering_id']),
        ('state', 'reject', ['peering_id'])
    ]

    module = AnsibleModule(argument_spec=argument_spec, required_if=required_if)

    if not HAS_BOTO3:
        module.fail_json(msg='json, botocore and boto3 are required.')
    state = module.params.get('state')
    peering_id = module.params.get('peering_id')
    vpc_id = module.params.get('vpc_id')
    peer_vpc_id = module.params.get('peer_vpc_id')
    try:
        region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)
        client = boto3_conn(module, conn_type='client', resource='ec2',
                            region=region, endpoint=ec2_url, **aws_connect_kwargs)
    except botocore.exceptions.NoCredentialsError as e:
        module.fail_json(msg="Can't authorize connection - " + str(e))

    if state == 'present':
        (changed, results) = create_peer_connection(client, module)
        module.exit_json(changed=changed, peering_id=results)
    elif state == 'absent':
        if not peering_id and (not vpc_id or not peer_vpc_id):
            module.fail_json(msg='state is absent but one of the following is missing: peering_id or [vpc_id, peer_vpc_id]')

        remove_peer_connection(client, module)
    else:
        (changed, results) = accept_reject(state, client, module)
        module.exit_json(changed=changed, peering_id=results)