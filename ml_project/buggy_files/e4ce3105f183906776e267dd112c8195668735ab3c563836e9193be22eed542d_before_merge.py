def create_instance(module, client, instance_name):
    """
    Create an instance

    module: Ansible module object
    client: authenticated lightsail connection object
    instance_name: name of instance to delete

    Returns a dictionary of instance information
    about the new instance.

    """

    changed = False

    # Check if instance already exists
    inst = None
    try:
        inst = _find_instance_info(client, instance_name)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] != 'NotFoundException':
            module.fail_json(msg='Error finding instance {0}, error: {1}'.format(instance_name, e))

    zone = module.params.get('zone')
    blueprint_id = module.params.get('blueprint_id')
    bundle_id = module.params.get('bundle_id')
    key_pair_name = module.params.get('key_pair_name')
    user_data = module.params.get('user_data')
    user_data = '' if user_data is None else user_data

    resp = None
    if inst is None:
        try:
            resp = client.create_instances(
                instanceNames=[
                    instance_name
                ],
                availabilityZone=zone,
                blueprintId=blueprint_id,
                bundleId=bundle_id,
                userData=user_data,
                keyPairName=key_pair_name,
            )
            resp = resp['operations'][0]
        except botocore.exceptions.ClientError as e:
            module.fail_json(msg='Unable to create instance {0}, error: {1}'.format(instance_name, e))
        changed = True

    inst = _find_instance_info(client, instance_name)

    return (changed, inst)