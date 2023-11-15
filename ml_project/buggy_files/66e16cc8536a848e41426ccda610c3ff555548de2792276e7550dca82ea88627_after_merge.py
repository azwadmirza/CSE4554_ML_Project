def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
        dhcp_options_id=dict(type='str', default=None),
        domain_name=dict(type='str', default=None),
        dns_servers=dict(type='list', default=None),
        ntp_servers=dict(type='list', default=None),
        netbios_name_servers=dict(type='list', default=None),
        netbios_node_type=dict(type='int', default=None),
        vpc_id=dict(type='str', default=None),
        delete_old=dict(type='bool', default=True),
        inherit_existing=dict(type='bool', default=False),
        tags=dict(type='dict', default=None, aliases=['resource_tags']),
        state=dict(type='str', default='present', choices=['present', 'absent'])
    )
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    params = module.params
    found = False
    changed = False
    new_options = collections.defaultdict(lambda: None)

    if not HAS_BOTO:
        module.fail_json(msg='boto is required for this module')

    region, ec2_url, boto_params = get_aws_connection_info(module)
    connection = connect_to_aws(boto.vpc, region, **boto_params)

    existing_options = None

    # First check if we were given a dhcp_options_id
    if not params['dhcp_options_id']:
        # No, so create new_options from the parameters
        if params['dns_servers'] is not None:
            new_options['domain-name-servers'] = params['dns_servers']
        if params['netbios_name_servers'] is not None:
            new_options['netbios-name-servers'] = params['netbios_name_servers']
        if params['ntp_servers'] is not None:
            new_options['ntp-servers'] = params['ntp_servers']
        if params['domain_name'] is not None:
            # needs to be a list for comparison with boto objects later
            new_options['domain-name'] = [params['domain_name']]
        if params['netbios_node_type'] is not None:
            # needs to be a list for comparison with boto objects later
            new_options['netbios-node-type'] = [str(params['netbios_node_type'])]
        # If we were given a vpc_id then we need to look at the options on that
        if params['vpc_id']:
            existing_options = fetch_dhcp_options_for_vpc(connection, params['vpc_id'])
            # if we've been asked to inherit existing options, do that now
            if params['inherit_existing']:
                if existing_options:
                    for option in ['domain-name-servers', 'netbios-name-servers', 'ntp-servers', 'domain-name', 'netbios-node-type']:
                        if existing_options.options.get(option) and new_options[option] != [] and (not new_options[option] or [''] == new_options[option]):
                            new_options[option] = existing_options.options.get(option)

            # Do the vpc's dhcp options already match what we're asked for? if so we are done
            if existing_options and new_options == existing_options.options:
                module.exit_json(changed=changed, new_options=new_options, dhcp_options_id=existing_options.id)

        # If no vpc_id was given, or the options don't match then look for an existing set using tags
        found, dhcp_option = match_dhcp_options(connection, params['tags'], new_options)

    # Now let's cover the case where there are existing options that we were told about by id
    # If a dhcp_options_id was supplied we don't look at options inside, just set tags (if given)
    else:
        supplied_options = connection.get_all_dhcp_options(filters={'dhcp-options-id': params['dhcp_options_id']})
        if len(supplied_options) != 1:
            if params['state'] != 'absent':
                module.fail_json(msg=" a dhcp_options_id was supplied, but does not exist")
        else:
            found = True
            dhcp_option = supplied_options[0]
            if params['state'] != 'absent' and params['tags']:
                ensure_tags(module, connection, dhcp_option.id, params['tags'], False, module.check_mode)

    # Now we have the dhcp options set, let's do the necessary

    # if we found options we were asked to remove then try to do so
    if params['state'] == 'absent':
        if not module.check_mode:
            if found:
                changed = remove_dhcp_options_by_id(connection, dhcp_option.id)
        module.exit_json(changed=changed, new_options={})

    # otherwise if we haven't found the required options we have something to do
    elif not module.check_mode and not found:

        # create some dhcp options if we weren't able to use existing ones
        if not found:
            # Convert netbios-node-type and domain-name back to strings
            if new_options['netbios-node-type']:
                new_options['netbios-node-type'] = new_options['netbios-node-type'][0]
            if new_options['domain-name']:
                new_options['domain-name'] = new_options['domain-name'][0]

            # create the new dhcp options set requested
            dhcp_option = connection.create_dhcp_options(
                new_options['domain-name'],
                new_options['domain-name-servers'],
                new_options['ntp-servers'],
                new_options['netbios-name-servers'],
                new_options['netbios-node-type'])

            # wait for dhcp option to be accessible
            found_dhcp_opt = False
            start_time = time()
            try:
                found_dhcp_opt = retry_not_found(connection.get_all_dhcp_options, dhcp_options_ids=[dhcp_option.id])
            except EC2ResponseError as e:
                module.fail_json(msg="Failed to describe DHCP options", exception=traceback.format_exc)
            if not found_dhcp_opt:
                module.fail_json(msg="Failed to wait for {0} to be available.".format(dhcp_option.id))

            changed = True
            if params['tags']:
                ensure_tags(module, connection, dhcp_option.id, params['tags'], False, module.check_mode)

    # If we were given a vpc_id, then attach the options we now have to that before we finish
    if params['vpc_id'] and not module.check_mode:
        changed = True
        connection.associate_dhcp_options(dhcp_option.id, params['vpc_id'])
        # and remove old ones if that was requested
        if params['delete_old'] and existing_options:
            remove_dhcp_options_by_id(connection, existing_options.id)

    module.exit_json(changed=changed, new_options=new_options, dhcp_options_id=dhcp_option.id)