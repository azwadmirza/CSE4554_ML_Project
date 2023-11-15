def disassociate_ipv6_cidr(conn, module, subnet, start_time):
    if subnet.get('assign_ipv6_address_on_creation'):
        ensure_assign_ipv6_on_create(conn, module, subnet, False, False, start_time)

    try:
        conn.disassociate_subnet_cidr_block(AssociationId=subnet['ipv6_association_id'])
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't disassociate ipv6 cidr block id {0} from subnet {1}"
                             .format(subnet['ipv6_association_id'], subnet['id']))

    # Wait for cidr block to be disassociated
    if module.params['wait']:
        filters = ansible_dict_to_boto3_filter_list(
            {'ipv6-cidr-block-association.state': ['disassociated'],
             'vpc-id': subnet['vpc_id']}
        )
        handle_waiter(conn, module, 'subnet_exists',
                      {'SubnetIds': [subnet['id']], 'Filters': filters}, start_time)