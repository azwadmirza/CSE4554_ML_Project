def restart_instance(module, client, instance_name):
    """
    Reboot an existing instance
    Wait will not apply here as this is an OS-level operation
    """

    changed = False

    inst = find_instance_info(module, client, instance_name, fail_if_not_found=True)

    try:
        client.reboot_instance(instanceName=instance_name)
        changed = True
    except botocore.exceptions.ClientError as e:
        module.fail_json_aws(e)

    module.exit_json(changed=changed, instance=camel_dict_to_snake_dict(inst))