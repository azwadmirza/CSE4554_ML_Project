def create_instance(module, client, instance_name):

    inst = find_instance_info(module, client, instance_name)
    if inst:
        module.exit_json(changed=False, instance=camel_dict_to_snake_dict(inst))
    else:
        create_params = {'instanceNames': [instance_name],
                         'availabilityZone': module.params.get('zone'),
                         'blueprintId': module.params.get('blueprint_id'),
                         'bundleId': module.params.get('bundle_id'),
                         'userData': module.params.get('user_data')}

        key_pair_name = module.params.get('key_pair_name')
        if key_pair_name:
            create_params['keyPairName'] = key_pair_name

        try:
            client.create_instances(**create_params)
        except botocore.exceptions.ClientError as e:
            module.fail_json_aws(e)

        wait = module.params.get('wait')
        if wait:
            desired_states = ['running']
            wait_for_instance_state(module, client, instance_name, desired_states)
        inst = find_instance_info(module, client, instance_name, fail_if_not_found=True)

        module.exit_json(changed=True, instance=camel_dict_to_snake_dict(inst))