def update_dhcp_opts(connection, module, vpc_obj, dhcp_id):
    if vpc_obj['DhcpOptionsId'] != dhcp_id:
        if not module.check_mode:
            try:
                connection.associate_dhcp_options(DhcpOptionsId=dhcp_id, VpcId=vpc_obj['VpcId'])
            except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
                module.fail_json_aws(e, msg="Failed to associate DhcpOptionsId {0}".format(dhcp_id))
        return True
    else:
        return False