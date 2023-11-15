def ensure_ipv6_cidr_block(conn, module, subnet, ipv6_cidr, check_mode):
    changed = False

    if subnet['ipv6_association_id'] and not ipv6_cidr:
        if not check_mode:
            disassociate_ipv6_cidr(conn, module, subnet)
        changed = True

    if ipv6_cidr:
        filters = ansible_dict_to_boto3_filter_list({'ipv6-cidr-block-association.ipv6-cidr-block': ipv6_cidr,
                                                     'vpc-id': subnet['vpc_id']})

        try:
            check_subnets = get_subnet_info(describe_subnets_with_backoff(conn, Filters=filters))
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't get subnet info")

        if check_subnets and check_subnets[0]['ipv6_cidr_block']:
            module.fail_json(msg="The IPv6 CIDR '{0}' conflicts with another subnet".format(ipv6_cidr))

        if subnet['ipv6_association_id']:
            if not check_mode:
                disassociate_ipv6_cidr(conn, module, subnet)
            changed = True

        try:
            if not check_mode:
                associate_resp = conn.associate_subnet_cidr_block(SubnetId=subnet['id'], Ipv6CidrBlock=ipv6_cidr)
            changed = True
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't associate ipv6 cidr {0} to {1}".format(ipv6_cidr, subnet['id']))

        if associate_resp.get('Ipv6CidrBlockAssociation', {}).get('AssociationId'):
            subnet['ipv6_association_id'] = associate_resp['Ipv6CidrBlockAssociation']['AssociationId']
            subnet['ipv6_cidr_block'] = associate_resp['Ipv6CidrBlockAssociation']['Ipv6CidrBlock']
            if subnet['ipv6_cidr_block_association_set']:
                subnet['ipv6_cidr_block_association_set'][0] = camel_dict_to_snake_dict(associate_resp['Ipv6CidrBlockAssociation'])
            else:
                subnet['ipv6_cidr_block_association_set'].append(camel_dict_to_snake_dict(associate_resp['Ipv6CidrBlockAssociation']))

    return changed