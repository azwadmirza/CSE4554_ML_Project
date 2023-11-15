def delete_instance(module, client, instance_name):
    """
    Terminates an instance

    module: Ansible module object
    client: authenticated lightsail connection object
    instance_name: name of instance to delete

    Returns a dictionary of instance information
    about the instance deleted (pre-deletion).

    If the instance to be deleted is running
    "changed" will be set to False.

    """

    # It looks like deleting removes the instance immediately, nothing to wait for
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

    # If instance doesn't exist, then return with 'changed:false'
    if not inst:
        return changed, {}

    # Wait for instance to exit transition state before deleting
    if wait:
        while wait_max > time.time() and inst is not None and inst['state']['name'] in ('pending', 'stopping'):
            try:
                time.sleep(5)
                inst = _find_instance_info(client, instance_name)
            except botocore.exceptions.ClientError as e:
                if e.response['ResponseMetadata']['HTTPStatusCode'] == "403":
                    module.fail_json(msg="Failed to delete instance {0}. Check that you have permissions to perform the operation.".format(instance_name),
                                     exception=traceback.format_exc())
                elif e.response['Error']['Code'] == "RequestExpired":
                    module.fail_json(msg="RequestExpired: Failed to delete instance {0}.".format(instance_name), exception=traceback.format_exc())
                # sleep and retry
                time.sleep(10)

    # Attempt to delete
    if inst is not None:
        while not changed and ((wait and wait_max > time.time()) or (not wait)):
            try:
                client.delete_instance(instanceName=instance_name)
                changed = True
            except botocore.exceptions.ClientError as e:
                module.fail_json(msg='Error deleting instance {0}, error: {1}'.format(instance_name, e))

    # Timed out
    if wait and not changed and wait_max <= time.time():
        module.fail_json(msg="wait for instance delete timeout at %s" % time.asctime())

    return (changed, inst)