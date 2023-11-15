def restart_instance(module, client, instance_name):
    """
    Reboot an existing instance

    module: Ansible module object
    client: authenticated lightsail connection object
    instance_name: name of instance to reboot

    Returns a dictionary of instance information
    about the restarted instance

    If the instance was not able to reboot,
    "changed" will be set to False.

    Wait will not apply here as this is an OS-level operation
    """
    wait = module.params.get('wait')
    wait_timeout = int(module.params.get('wait_timeout'))
    wait_max = time.time() + wait_timeout

    changed = False

    inst = None
    try:
        inst = _find_instance_info(client, instance_name)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] != 'NotFoundException':
            module.fail_json(msg='Error finding instance {0}, error: {1}'.format(instance_name, e))

    # Wait for instance to exit transition state before state change
    if wait:
        while wait_max > time.time() and inst is not None and inst['state']['name'] in ('pending', 'stopping'):
            try:
                time.sleep(5)
                inst = _find_instance_info(client, instance_name)
            except botocore.exceptions.ClientError as e:
                if e.response['ResponseMetadata']['HTTPStatusCode'] == "403":
                    module.fail_json(msg="Failed to restart instance {0}. Check that you have permissions to perform the operation.".format(instance_name),
                                     exception=traceback.format_exc())
                elif e.response['Error']['Code'] == "RequestExpired":
                    module.fail_json(msg="RequestExpired: Failed to restart instance {0}.".format(instance_name), exception=traceback.format_exc())
                time.sleep(3)

    # send reboot
    if inst is not None:
        try:
            client.reboot_instance(instanceName=instance_name)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] != 'NotFoundException':
                module.fail_json(msg='Unable to reboot instance {0}, error: {1}'.format(instance_name, e))
        changed = True

    return (changed, inst)