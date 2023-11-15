def delete_instance(module, client, instance_name):

    changed = False

    inst = find_instance_info(module, client, instance_name)
    if inst is None:
        module.exit_json(changed=changed, instance={})

    # Wait for instance to exit transition state before deleting
    desired_states = ['running', 'stopped']
    wait_for_instance_state(module, client, instance_name, desired_states)

    try:
        client.delete_instance(instanceName=instance_name)
        changed = True
    except botocore.exceptions.ClientError as e:
        module.fail_json_aws(e)

    module.exit_json(changed=changed, instance=camel_dict_to_snake_dict(inst))